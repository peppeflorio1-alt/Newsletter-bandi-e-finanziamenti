# -*- coding: utf-8 -*-
"""
stato_bando.py
---------------
Ogni sito descrive lo stato di un bando a modo suo (es. "In corso",
"Chiuso", "Aperto", "In apertura"...). Questo modulo prova a tradurre
quel testo in una delle tre categorie che usiamo nella pagina:

    "aperto"             -> il bando accetta domande adesso
    "prossima_apertura"  -> il bando aprira' a breve, non ancora
    "chiuso"             -> il bando e' scaduto o concluso

Se il testo non e' riconosciuto (o manca del tutto), restituisce None:
in quel caso chi chiama questa funzione decide un comportamento di
riserva (in genera_pagina.py, si guarda alla data di scadenza).
"""

PAROLE_CHIUSO = ["chius", "scadut", "conclus", "terminat", "revocat"]
PAROLE_PROSSIMA_APERTURA = ["prossim", "in apertura", "non ancora aperto", "futur"]
PAROLE_APERTO = ["aperto", "in corso", "attivo", "pubblicat"]


def classifica(testo_stato: str | None) -> str | None:
    if not testo_stato:
        return None

    testo = testo_stato.strip().lower()

    if any(parola in testo for parola in PAROLE_CHIUSO):
        return "chiuso"
    if any(parola in testo for parola in PAROLE_PROSSIMA_APERTURA):
        return "prossima_apertura"
    if any(parola in testo for parola in PAROLE_APERTO):
        return "aperto"

    return None
