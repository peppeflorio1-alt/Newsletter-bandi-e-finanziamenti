# -*- coding: utf-8 -*-
"""
fetch_wordpress.py
--------------------
Legge una fonte di tipo "wordpress": molte fondazioni (bancarie e private)
usano WordPress per il loro sito, e WordPress offre di serie un archivio
dati in formato JSON per ogni tipo di contenuto (articoli, ma anche tipi
personalizzati come "bando").

Come riconoscere se un sito usa WordPress e ha un tipo di contenuto
"bando" (utile per aggiungere nuove fonti): prova ad aprire, nel browser,
questo indirizzo (sostituendo il dominio):

    https://www.esempio-fondazione.it/wp-json/wp/v2/types

Se il sito e' WordPress, si apre un elenco di parole come "post", "page",
e a volte anche "bando" o simili: quella e' la lista dei tipi di
contenuto disponibili. Se compare "bando", prova poi:

    https://www.esempio-fondazione.it/wp-json/wp/v2/bando

Se vedi un elenco di bandi in JSON, la fonte e' pronta per essere
configurata cosi' in sources.yaml:

    - nome: "Nome della fondazione"
      livello: regione
      area: "Nome Regione"
      tipo: wordpress
      url: "https://www.esempio-fondazione.it"   # solo il dominio
      tipo_contenuto: "bando"                     # il nome trovato sopra

NOTA: la maggior parte dei siti WordPress non espone in modo strutturato
la data di scadenza o lo stato "aperto/chiuso" di un bando (a differenza
dei siti Plone visti finora): per queste fonti la newsletter assume che,
se il sito lo elenca ancora nella sua pagina bandi, il bando sia ancora
valido. Se un domani la fondazione lascia online un bando ormai chiuso,
potrebbe comparire per errore: in tal caso si puo' escludere manualmente
quella fonte o segnalarmelo per affinare la configurazione.
"""

import re
from html import unescape

import requests

INTESTAZIONI = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
}

ELEMENTI_PER_PAGINA = 20
MASSIMO_PAGINE = 10  # sicurezza: al massimo 200 elementi per fonte


def _pulisci_html(testo_html: str) -> str:
    """Toglie i tag HTML e decodifica caratteri come &#8211; -> 'e' cosi' via,
    per ottenere un testo semplice da mettere nel riassunto."""
    senza_tag = re.sub(r"<[^>]+>", " ", testo_html or "")
    testo = unescape(senza_tag)
    return re.sub(r"\s+", " ", testo).strip()


def fetch(fonte: dict) -> list[dict]:
    risultati = []

    base_url = fonte["url"].rstrip("/")
    tipo_contenuto = fonte.get("tipo_contenuto", "posts")
    endpoint = f"{base_url}/wp-json/wp/v2/{tipo_contenuto}"

    for pagina in range(1, MASSIMO_PAGINE + 1):
        try:
            risposta = requests.get(
                endpoint,
                params={"page": pagina, "per_page": ELEMENTI_PER_PAGINA},
                headers=INTESTAZIONI,
                timeout=20,
            )
            if risposta.status_code == 400:
                # WordPress risponde 400 quando si chiede una pagina oltre
                # l'ultima disponibile: e' il segnale normale di "fine".
                break
            risposta.raise_for_status()
        except requests.RequestException as errore:
            print(f"[ATTENZIONE] Impossibile leggere '{fonte['nome']}' ({errore})")
            break

        elementi = risposta.json()
        if not elementi:
            break

        for elemento in elementi:
            titolo = _pulisci_html(elemento.get("title", {}).get("rendered", ""))
            link = elemento.get("link", "")
            if not titolo or not link:
                continue

            riassunto_completo = _pulisci_html(elemento.get("content", {}).get("rendered", ""))

            risultati.append({
                "titolo": titolo,
                "link": link,
                "riassunto": riassunto_completo[:400],
                "data_pubblicazione": elemento.get("date"),
                "scadenza": None,      # vedi nota nel commento in cima al file
                "stato_testo": None,   # idem
                "ente": fonte["nome"],
                "livello": fonte["livello"],
                "area": fonte.get("area"),
            })

        if len(elementi) < ELEMENTI_PER_PAGINA:
            break  # ultima pagina raggiunta

    return risultati
