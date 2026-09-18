# -*- coding: utf-8 -*-
"""
fetch_html.py
-------------
Legge una fonte di tipo "html": una pagina web normale, senza feed RSS.

Per queste fonti, in sources.yaml devi indicare dei "selettori CSS", cioe'
delle istruzioni tipo "cerca ogni <div class='bando'>, dentro prendi il
testo del link <a>". Il README spiega come trovare questi selettori con
il tasto destro del mouse -> "Ispeziona", senza scrivere codice.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

INTESTAZIONI = {
    # Alcuni siti pubblici bloccano le richieste che non sembrano
    # provenire da un browser vero. Questo risolve la maggior parte dei casi.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def _testo_o_vuoto(elemento):
    return elemento.get_text(strip=True) if elemento else ""


def fetch(fonte: dict) -> list[dict]:
    """
    Scarica una pagina HTML e ne estrae i bandi secondo i selettori
    indicati in sources.yaml sotto la chiave "selettori".

    Ritorna una lista di dizionari nello stesso formato di fetch_rss.fetch().
    """
    risultati = []
    selettori = fonte.get("selettori")

    if not selettori:
        print(f"[ATTENZIONE] La fonte HTML '{fonte['nome']}' non ha 'selettori' in sources.yaml: saltata.")
        return risultati

    try:
        risposta = requests.get(fonte["url"], headers=INTESTAZIONI, timeout=20)
        risposta.raise_for_status()
    except requests.RequestException as errore:
        print(f"[ATTENZIONE] Impossibile scaricare la pagina: {fonte['nome']} ({errore})")
        return risultati

    zuppa = BeautifulSoup(risposta.text, "html.parser")
    schede = zuppa.select(selettori["contenitore_elemento"])

    for scheda in schede:
        elemento_titolo = scheda.select_one(selettori.get("titolo", ""))
        elemento_link = scheda.select_one(selettori.get("link", selettori.get("titolo", "")))
        elemento_data = scheda.select_one(selettori.get("data", "")) if selettori.get("data") else None
        elemento_riassunto = scheda.select_one(selettori.get("riassunto", "")) if selettori.get("riassunto") else None

        titolo = _testo_o_vuoto(elemento_titolo)
        link_relativo = elemento_link.get("href") if elemento_link else None

        if not titolo or not link_relativo:
            continue

        # Trasforma un link relativo (es. "/bandi/123") in un link completo
        link = urljoin(fonte["url"], link_relativo)

        risultati.append({
            "titolo": titolo,
            "link": link,
            "riassunto": _testo_o_vuoto(elemento_riassunto),
            "data_pubblicazione": _testo_o_vuoto(elemento_data) or None,
            "ente": fonte["nome"],
            "livello": fonte["livello"],
        })

    return risultati
