# -*- coding: utf-8 -*-
"""
stato.py
--------
Tiene la "memoria" della newsletter tra un giorno e l'altro:
- ricorda quando un bando e' apparso per la prima volta (per segnarlo "NUOVO")
- toglie dalla pagina i bandi che non compaiono piu' da troppi giorni
  (probabilmente scaduti o rimossi dal sito di origine)

Tutto viene salvato in data/stato.json, che viene aggiornato ad ogni
esecuzione e "ricordato" da un giorno all'altro perche' GitHub Actions lo
ricommitta nel repository (vedi .github/workflows/daily.yml).
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

PERCORSO_STATO = Path(__file__).resolve().parent.parent / "data" / "stato.json"


def _id_bando(bando: dict) -> str:
    """Un identificativo stabile per il bando, basato sul link (che di solito non cambia)."""
    return hashlib.sha1(bando["link"].encode("utf-8")).hexdigest()


def carica_stato() -> dict:
    if PERCORSO_STATO.exists():
        with open(PERCORSO_STATO, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def salva_stato(stato: dict) -> None:
    PERCORSO_STATO.parent.mkdir(parents=True, exist_ok=True)
    with open(PERCORSO_STATO, "w", encoding="utf-8") as file:
        json.dump(stato, file, ensure_ascii=False, indent=2, sort_keys=True)


def aggiorna_stato_e_arricchisci(bandi_trovati_oggi: list[dict], stato: dict, giorni_di_permanenza: int) -> list[dict]:
    """
    Confronta i bandi trovati oggi con lo stato salvato:
    - se un bando e' nuovo, lo aggiunge allo stato con data di oggi
    - se un bando esisteva gia', aggiorna "ultima_volta_visto"
    - aggiunge a ogni bando i campi "nuovo_oggi" e "primo_avvistamento"

    Ritorna la lista di bandi DA MOSTRARE nella pagina: quelli trovati oggi
    PIU' quelli visti negli ultimi `giorni_di_permanenza` giorni anche se
    oggi la fonte non li elenca piu' (es. pagina che mostra solo gli ultimi 10).
    """
    oggi = datetime.utcnow().date().isoformat()
    id_trovati_oggi = set()

    for bando in bandi_trovati_oggi:
        identificativo = _id_bando(bando)
        id_trovati_oggi.add(identificativo)

        if identificativo not in stato:
            stato[identificativo] = {
                "primo_avvistamento": oggi,
                "dati": bando,
            }
        stato[identificativo]["ultima_volta_visto"] = oggi
        stato[identificativo]["dati"] = bando  # aggiorna eventuali dettagli cambiati

    # Rimuove dallo stato i bandi troppo vecchi (non visti da troppo tempo)
    soglia = (datetime.utcnow().date() - timedelta(days=giorni_di_permanenza)).isoformat()
    identificativi_da_tenere = {
        identificativo: voce
        for identificativo, voce in stato.items()
        if voce["ultima_volta_visto"] >= soglia
    }
    stato.clear()
    stato.update(identificativi_da_tenere)

    # Costruisce la lista finale da mostrare nella pagina
    bandi_da_mostrare = []
    for identificativo, voce in stato.items():
        bando = dict(voce["dati"])
        bando["primo_avvistamento"] = voce["primo_avvistamento"]
        bando["nuovo_oggi"] = voce["primo_avvistamento"] == oggi
        bandi_da_mostrare.append(bando)

    return bandi_da_mostrare
