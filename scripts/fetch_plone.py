# -*- coding: utf-8 -*-
"""
fetch_plone.py
---------------
Legge una fonte di tipo "plone": molti siti di Regioni e Comuni italiani
sono costruiti con una piattaforma chiamata Plone (spesso nel template
"Design Italia" di AGID) e offrono un vero archivio dati in formato JSON,
molto piu' affidabile di uno scraping HTML.

Come riconoscere se un sito usa Plone (utile per aggiungere nuove fonti):
apri la pagina dei bandi, apri gli strumenti sviluppatore del browser
(F12) -> scheda "Network"/"Rete", ricarica la pagina, e cerca richieste
che contengono "++api++" nell'indirizzo. Se le trovi, il sito e' Plone e
puoi usare questo connettore invece di fetch_html.py.

In sources.yaml, una fonte di questo tipo si scrive cosi':

    - nome: "Nome del sito"
      livello: regione
      tipo: plone
      url: "https://www.esempio-regione.it"          # solo il dominio
      percorso: "/sezione/sottosezione-bandi"          # il percorso della pagina bandi
      tipi_contenuto: ["Bando"]                        # facoltativo, vedi sotto

`tipi_contenuto` filtra solo i contenuti "veri" bandi, escludendo le
pagine di categoria/sottosezione. Se non sai quale valore usare, lascialo
vuoto: verranno presi tutti i contenuti sotto quel percorso (potrebbe
includere qualche pagina che non e' un bando vero).
"""

import requests

INTESTAZIONI = {"Content-Type": "application/json", "Accept": "application/json"}

DIMENSIONE_PAGINA = 50
MASSIMO_PAGINE = 10  # sicurezza: al massimo 500 elementi per fonte, per evitare loop infiniti


def fetch(fonte: dict) -> list[dict]:
    risultati = []

    base_url = fonte["url"].rstrip("/")
    percorso = fonte["percorso"].strip("/")
    tipi_contenuto = fonte.get("tipi_contenuto")

    endpoint = f"{base_url}/++api++/{percorso}/@querystring-search"

    query = [
        {"i": "path", "o": "plone.app.querystring.operation.string.path", "v": f"/{percorso}"}
    ]
    if tipi_contenuto:
        query.append({
            "i": "portal_type",
            "o": "plone.app.querystring.operation.selection.any",
            "v": tipi_contenuto,
        })

    b_start = 0
    for _ in range(MASSIMO_PAGINE):
        corpo = {
            "query": query,
            "sort_on": "effective",
            "sort_order": "descending",
            "b_size": DIMENSIONE_PAGINA,
            "b_start": b_start,
        }
        try:
            risposta = requests.post(endpoint, json=corpo, headers=INTESTAZIONI, timeout=20)
            risposta.raise_for_status()
        except requests.RequestException as errore:
            print(f"[ATTENZIONE] Impossibile leggere '{fonte['nome']}' ({errore})")
            break

        dati = risposta.json()

        if "error" in dati:
            print(f"[ATTENZIONE] La fonte '{fonte['nome']}' ha risposto con un errore: {dati['error'].get('message')}")
            break

        elementi = dati.get("items", [])
        if not elementi:
            break

        for elemento in elementi:
            titolo = (elemento.get("title") or "").strip()
            link = elemento.get("@id", "")
            if not titolo or not link:
                continue

            risultati.append({
                "titolo": titolo,
                "link": link,
                "riassunto": elemento.get("description") or "",
                "data_pubblicazione": elemento.get("effective") or elemento.get("Date"),
                "ente": fonte["nome"],
                "livello": fonte["livello"],
            })

        b_start += DIMENSIONE_PAGINA
        if b_start >= dati.get("items_total", 0):
            break

    return risultati
