# -*- coding: utf-8 -*-
"""
filters.py
----------
Decide quali bandi tenere, confrontando titolo + riassunto con la lista
di parole chiave scritta in config/sources.yaml.
"""

import unicodedata


def _normalizza(testo: str) -> str:
    """Minuscolo e senza accenti, per confronti piu' tolleranti."""
    testo = testo.lower()
    testo = unicodedata.normalize("NFKD", testo)
    testo = "".join(carattere for carattere in testo if not unicodedata.combining(carattere))
    return testo


def filtra_per_parole_chiave(bandi: list[dict], parole_chiave: list[str]) -> list[dict]:
    """
    Ritorna solo i bandi il cui titolo o riassunto contiene almeno una
    delle parole_chiave (confronto senza maiuscole/accenti).
    """
    parole_normalizzate = [_normalizza(parola) for parola in parole_chiave]
    bandi_filtrati = []

    for bando in bandi:
        testo_completo = _normalizza(f"{bando.get('titolo', '')} {bando.get('riassunto', '')}")
        if any(parola in testo_completo for parola in parole_normalizzate):
            bandi_filtrati.append(bando)

    return bandi_filtrati
