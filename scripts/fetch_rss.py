# -*- coding: utf-8 -*-
"""
fetch_rss.py
------------
Legge una fonte di tipo "rss" e restituisce una lista di bandi grezzi.

Non serve capire tutto il codice per usare il progetto: questo file viene
chiamato automaticamente da main.py. Lo si tocca solo se un giorno si vuole
cambiare COME vengono lette le fonti RSS (raro).
"""

import feedparser
from datetime import datetime


def fetch(fonte: dict) -> list[dict]:
    """
    Scarica e interpreta un feed RSS/Atom.

    Parametri:
        fonte: il dizionario della fonte cosi' come scritto in sources.yaml
               (deve avere almeno "url", "nome", "livello")

    Ritorna:
        una lista di dizionari, ognuno con:
        titolo, link, riassunto, data_pubblicazione, ente, livello
    """
    risultati = []

    feed = feedparser.parse(fonte["url"])

    # feedparser non lancia un'eccezione se l'URL e' sbagliato: mette
    # semplicemente "bozo" a True. Lo segnaliamo ma non blocchiamo tutto
    # lo script per una singola fonte che non funziona.
    if feed.bozo and not feed.entries:
        print(f"[ATTENZIONE] Impossibile leggere il feed RSS: {fonte['nome']} ({fonte['url']})")
        return risultati

    for voce in feed.entries:
        titolo = voce.get("title", "").strip()
        link = voce.get("link", "").strip()
        riassunto = voce.get("summary", "") or voce.get("description", "")

        data_pubblicazione = None
        if voce.get("published_parsed"):
            data_pubblicazione = datetime(*voce.published_parsed[:6]).isoformat()
        elif voce.get("updated_parsed"):
            data_pubblicazione = datetime(*voce.updated_parsed[:6]).isoformat()

        if not titolo or not link:
            continue

        risultati.append({
            "titolo": titolo,
            "link": link,
            "riassunto": riassunto,
            "data_pubblicazione": data_pubblicazione,
            "scadenza": None,  # i feed RSS di solito non indicano una scadenza separata
            "ente": fonte["nome"],
            "livello": fonte["livello"],
        })

    return risultati
