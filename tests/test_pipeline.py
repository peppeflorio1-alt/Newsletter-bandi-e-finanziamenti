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
import fetch_wordpress
import filters
import stato
import stato_bando
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


def test_pagina_mostra_solo_aperti_e_scadenza():
    """Verifica che genera_pagina.py:
    - mostri la scadenza in modo leggibile per un bando ancora aperto
    - ESCLUDA dalla pagina un bando gia' scaduto (comportamento voluto:
      la newsletter deve mostrare solo aperti o di prossima apertura)."""
    bando_aperto = {
        "titolo": "Bando ancora aperto", "link": "https://esempio.it/1",
        "riassunto": "", "ente": "Prova", "livello": "regione", "area": "Emilia-Romagna",
        "primo_avvistamento": "2026-01-01", "nuovo_oggi": False,
        "scadenza": "2099-12-31T00:00:00+00:00", "stato_testo": None,
    }
    bando_chiuso = {
        "titolo": "Bando ormai chiuso", "link": "https://esempio.it/2",
        "riassunto": "", "ente": "Prova", "livello": "regione", "area": "Emilia-Romagna",
        "primo_avvistamento": "2026-01-01", "nuovo_oggi": False,
        "scadenza": "2020-01-01T00:00:00+00:00", "stato_testo": None,
    }
    bando_in_apertura = {
        "titolo": "Bando di prossima apertura", "link": "https://esempio.it/3",
        "riassunto": "", "ente": "Prova", "livello": "italia", "area": None,
        "primo_avvistamento": "2026-01-01", "nuovo_oggi": False,
        "scadenza": None, "stato_testo": "In apertura",
    }

    percorso = genera_pagina.genera([bando_aperto, bando_chiuso, bando_in_apertura], "Test scadenze")
    contenuto = percorso.read_text(encoding="utf-8")

    assert "Bando ancora aperto" in contenuto
    assert "31/12/2099" in contenuto
    assert "Bando di prossima apertura" in contenuto
    assert "In apertura" in contenuto
    assert "Bando ormai chiuso" not in contenuto, "Un bando scaduto NON deve comparire nella pagina"
    print("OK: genera_pagina.py mostra solo bandi aperti/in apertura, con scadenza leggibile")


def test_stato_bando():
    assert stato_bando.classifica("Chiuso") == "chiuso"
    assert stato_bando.classifica("In corso") == "aperto"
    assert stato_bando.classifica("In apertura") == "prossima_apertura"
    assert stato_bando.classifica(None) is None
    assert stato_bando.classifica("testo non riconosciuto") is None
    print("OK: stato_bando.py classifica correttamente i testi comuni")


def test_tab_monitorata_ma_vuota():
    """Se una fonte e' configurata (es. Emilia-Romagna) ma oggi non ha
    nessun bando aperto da mostrare, la tab deve comunque comparire con un
    messaggio, non sparire del tutto."""
    bando_lombardia = {
        "titolo": "Bando Lombardia aperto", "link": "https://esempio.it/1",
        "riassunto": "", "ente": "Prova", "livello": "regione", "area": "Lombardia",
        "primo_avvistamento": "2026-01-01", "nuovo_oggi": False,
        "scadenza": "2099-12-31T00:00:00+00:00", "stato_testo": None,
    }
    percorso = genera_pagina.genera(
        [bando_lombardia], "Test tab vuota",
        chiavi_monitorate={"Lombardia", "Emilia-Romagna"},
    )
    contenuto = percorso.read_text(encoding="utf-8")
    assert "Bando Lombardia aperto" in contenuto
    assert "Emilia-Romagna" in contenuto
    assert "Nessun bando aperto o di prossima apertura al momento in Emilia-Romagna" in contenuto
    print("OK: le tab monitorate ma vuote mostrano un messaggio invece di sparire")


def test_fetch_wordpress():
    """Verifica fetch_wordpress.py con una risposta finta (stessa forma di
    quella osservata davvero su Fondazione Cariplo/Carisbo), senza rete."""
    pagina_1 = [{
        "title": {"rendered": "Musei e accessibilit&#224; universale"},
        "link": "https://esempio-fondazione.it/bando/musei/",
        "content": {"rendered": "<p>Un bando di prova sulla <b>cultura</b>.</p>"},
        "date": "2026-05-01T10:00:00",
    }]

    fonte_finta = {
        "nome": "Fondazione di prova", "livello": "regione", "area": "Lombardia",
        "url": "https://esempio-fondazione.it", "tipo_contenuto": "bando",
    }

    with patch("fetch_wordpress.requests.get") as mock_get:
        risposta_pagina_1 = MagicMock()
        risposta_pagina_1.status_code = 200
        risposta_pagina_1.json.return_value = pagina_1
        risposta_pagina_1.raise_for_status.return_value = None

        risposta_pagina_2 = MagicMock()
        risposta_pagina_2.status_code = 400  # simula "non c'e' una pagina 2"

        mock_get.side_effect = [risposta_pagina_1, risposta_pagina_2]

        bandi = fetch_wordpress.fetch(fonte_finta)

    assert len(bandi) == 1
    assert bandi[0]["titolo"] == "Musei e accessibilità universale"
    assert "Un bando di prova sulla cultura" in bandi[0]["riassunto"]
    print("OK: fetch_wordpress.py interpreta correttamente la risposta JSON")


if __name__ == "__main__":
    bandi_filtrati = test_fetch_rss_e_filtro()
    test_stato_e_pagina(bandi_filtrati)
    test_fetch_plone()
    test_fetch_wordpress()
    test_pagina_mostra_solo_aperti_e_scadenza()
    test_stato_bando()
    test_tab_monitorata_ma_vuota()
    print("\nTutti i test sono passati.")
