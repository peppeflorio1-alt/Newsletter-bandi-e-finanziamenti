# -*- coding: utf-8 -*-
"""
test_pipeline.py
-----------------
Test "fatto in casa" (senza framework) che verifica che i pezzi principali
funzionino insieme, usando un feed RSS finto salvato su disco invece di
scaricare qualcosa da internet. Utile per controllare che il codice non
sia rotto dopo una modifica.

Si lancia con:  python tests/test_pipeline.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import fetch_rss
import filters
import stato
import genera_pagina

PERCORSO_FEED_FINTO = Path(__file__).resolve().parent / "fixtures" / "feed_finto.xml"


def test_fetch_rss_e_filtro():
    fonte_finta = {
        "nome": "Fonte di prova",
        "livello": "regione",
        "url": str(PERCORSO_FEED_FINTO),
    }
    bandi = fetch_rss.fetch(fonte_finta)
    assert len(bandi) == 3, f"Attesi 3 elementi dal feed finto, trovati {len(bandi)}"

    parole_chiave = ["cultura", "culturali", "partecipazione", "democrazia"]
    bandi_filtrati = filters.filtra_per_parole_chiave(bandi, parole_chiave)
    assert len(bandi_filtrati) == 2, f"Attesi 2 bandi dopo il filtro, trovati {len(bandi_filtrati)}"
    print("OK: fetch_rss + filters funzionano correttamente")
    return bandi_filtrati


def test_stato_e_pagina(bandi_filtrati):
    stato_vuoto = {}
    bandi_arricchiti = stato.aggiorna_stato_e_arricchisci(bandi_filtrati, stato_vuoto, giorni_di_permanenza=60)
    assert all("nuovo_oggi" in b for b in bandi_arricchiti)
    assert all(b["nuovo_oggi"] for b in bandi_arricchiti), "Al primo avvistamento devono essere tutti 'nuovi'"
    print("OK: stato.py assegna correttamente 'nuovo_oggi'")

    percorso = genera_pagina.genera(bandi_arricchiti, "Test pagina")
    assert percorso.exists()
    contenuto = percorso.read_text(encoding="utf-8")
    assert "Bando per il restauro" in contenuto
    assert "NUOVO" in contenuto
    print(f"OK: pagina generata correttamente in {percorso}")


if __name__ == "__main__":
    bandi_filtrati = test_fetch_rss_e_filtro()
    test_stato_e_pagina(bandi_filtrati)
    print("\nTutti i test sono passati.")
