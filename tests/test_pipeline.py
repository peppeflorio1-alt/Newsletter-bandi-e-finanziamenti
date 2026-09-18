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

from unittest.mock import patch, MagicMock

import fetch_rss
import fetch_plone
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


def test_fetch_plone():
    """Verifica fetch_plone.py con una risposta finta (stessa forma di quella
    osservata davvero su regione.emilia-romagna.it), senza usare la rete."""
    risposta_finta = {
        "items_total": 1,
        "items": [
            {
                "title": "Bando cultura di prova",
                "@id": "https://esempio-regione.it/bandi/bando-cultura-di-prova",
                "description": "Descrizione di prova per il bando culturale.",
                "effective": "2026-05-20T13:52:23+00:00",
                "@type": "Bando",
            }
        ],
    }

    fonte_finta = {
        "nome": "Fonte Plone di prova",
        "livello": "regione",
        "url": "https://esempio-regione.it",
        "percorso": "/bandi",
        "tipi_contenuto": ["Bando"],
    }

    with patch("fetch_plone.requests.post") as mock_post:
        mock_risposta = MagicMock()
        mock_risposta.json.return_value = risposta_finta
        mock_risposta.raise_for_status.return_value = None
        mock_post.return_value = mock_risposta

        bandi = fetch_plone.fetch(fonte_finta)

    assert len(bandi) == 1, f"Atteso 1 bando, trovati {len(bandi)}"
    assert bandi[0]["titolo"] == "Bando cultura di prova"
    assert bandi[0]["link"] == "https://esempio-regione.it/bandi/bando-cultura-di-prova"
    # la scadenza va recuperata con una seconda richiesta (mockata anch'essa):
    # qui non la mocked separatamente quindi ci si aspetta un fallimento
    # "silenzioso" (None), che e' il comportamento corretto in caso di errore.
    assert bandi[0]["scadenza"] is None
    print("OK: fetch_plone.py interpreta correttamente la risposta JSON")


def test_pagina_mostra_scadenza():
    """Verifica che genera_pagina.py trasformi una scadenza in data leggibile
    e segnali correttamente se e' gia' passata."""
    bando_futuro = {
        "titolo": "Bando con scadenza futura", "link": "https://esempio.it/1",
        "riassunto": "", "ente": "Prova", "livello": "regione",
        "primo_avvistamento": "2026-01-01", "nuovo_oggi": False,
        "scadenza": "2099-12-31T00:00:00+00:00",
    }
    bando_scaduto = {
        "titolo": "Bando gia' scaduto", "link": "https://esempio.it/2",
        "riassunto": "", "ente": "Prova", "livello": "regione",
        "primo_avvistamento": "2026-01-01", "nuovo_oggi": False,
        "scadenza": "2020-01-01T00:00:00+00:00",
    }
    percorso = genera_pagina.genera([bando_futuro, bando_scaduto], "Test scadenze")
    contenuto = percorso.read_text(encoding="utf-8")
    assert "31/12/2099" in contenuto
    assert "01/01/2020" in contenuto
    assert "Scadenza superata" in contenuto
    print("OK: genera_pagina.py calcola correttamente le scadenze")


if __name__ == "__main__":
    bandi_filtrati = test_fetch_rss_e_filtro()
    test_stato_e_pagina(bandi_filtrati)
    test_fetch_plone()
    test_pagina_mostra_scadenza()
    print("\nTutti i test sono passati.")
