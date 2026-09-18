# -*- coding: utf-8 -*-
"""
genera_pagina.py
----------------
Prende la lista finale di bandi, tiene solo quelli aperti o di prossima
apertura, li raggruppa in tab (una per regione, poi Italia, poi Europa)
e produce il file docs/index.html, la pagina che GitHub Pages pubblica.
"""

from datetime import datetime
from pathlib import Path
from dateutil import parser as analizzatore_date
from jinja2 import Environment, FileSystemLoader

import stato_bando

CARTELLA_TEMPLATE = Path(__file__).resolve().parent.parent / "templates"
CARTELLA_OUTPUT = Path(__file__).resolve().parent.parent / "docs"

# Le regioni target compaiono per prime, nell'ordine indicato; qualunque
# altra area (altre regioni, altri comuni) viene aggiunta dopo in ordine
# alfabetico. "Italia" ed "Europa" restano sempre le ultime due tab.
REGIONI_PRIORITARIE = ["Emilia-Romagna", "Lombardia", "Piemonte"]
TAB_FINALI = ["Italia", "Europa", "Internazionale"]


def _leggibile_e_scaduta(valore_scadenza) -> tuple[str | None, bool]:
    """Trasforma una scadenza (che puo' arrivare in formati diversi a
    seconda della fonte) in una data leggibile tipo 21/10/2026, e dice
    anche se quella data e' gia' passata rispetto ad oggi."""
    if not valore_scadenza:
        return None, False
    try:
        data = analizzatore_date.parse(str(valore_scadenza))
    except (ValueError, TypeError, OverflowError):
        return None, False
    scaduta = data.date() < datetime.now().date()
    return data.strftime("%d/%m/%Y"), scaduta


def _tab_del_bando(bando: dict) -> str:
    """Decide in quale tab finisce un bando: una tab per ogni area/regione
    (i bandi di un Comune finiscono nella tab della loro stessa regione),
    altrimenti Italia / Europa / Internazionale in base al livello."""
    if bando["livello"] in ("regione", "comune") and bando.get("area"):
        return bando["area"]
    if bando["livello"] == "italia":
        return "Italia"
    if bando["livello"] == "europa":
        return "Europa"
    if bando["livello"] == "internazionale":
        return "Internazionale"
    return "Altro"


def _ordina_le_tab(chiavi_presenti) -> list[str]:
    ordine = [r for r in REGIONI_PRIORITARIE if r in chiavi_presenti]
    altre_regioni = sorted(
        k for k in chiavi_presenti if k not in REGIONI_PRIORITARIE and k not in TAB_FINALI and k != "Altro"
    )
    ordine.extend(altre_regioni)
    ordine.extend(t for t in TAB_FINALI if t in chiavi_presenti)
    if "Altro" in chiavi_presenti:
        ordine.append("Altro")
    return ordine


def genera(bandi: list[dict], titolo_pagina: str) -> Path:
    """
    Tiene solo i bandi aperti o di prossima apertura, li raggruppa in tab
    e scrive docs/index.html. Ritorna il percorso del file scritto.
    """
    bandi_da_mostrare = []
    for bando in bandi:
        bando["scadenza_leggibile"], bando["scaduto"] = _leggibile_e_scaduta(bando.get("scadenza"))

        categoria_stato = stato_bando.classifica(bando.get("stato_testo"))
        if categoria_stato is None:
            # Nessuna indicazione esplicita di stato da parte della fonte:
            # ci basiamo sulla scadenza. Senza scadenza, o con scadenza
            # futura, consideriamo il bando ancora valido da mostrare.
            categoria_stato = "chiuso" if bando["scaduto"] else "aperto"
        bando["stato_categoria"] = categoria_stato

        if categoria_stato in ("aperto", "prossima_apertura"):
            bandi_da_mostrare.append(bando)

    bandi_per_tab: dict[str, list[dict]] = {}
    for bando in bandi_da_mostrare:
        bandi_per_tab.setdefault(_tab_del_bando(bando), []).append(bando)

    for chiave in bandi_per_tab:
        bandi_per_tab[chiave].sort(
            key=lambda b: (b.get("nuovo_oggi", False), b.get("primo_avvistamento", "")),
            reverse=True,
        )

    ordine_tab = _ordina_le_tab(bandi_per_tab.keys())

    ambiente = Environment(loader=FileSystemLoader(str(CARTELLA_TEMPLATE)))
    modello = ambiente.get_template("pagina.html.jinja")

    html = modello.render(
        titolo_pagina=titolo_pagina,
        data_aggiornamento=datetime.now().strftime("%d/%m/%Y %H:%M"),
        numero_totale_bandi=len(bandi_da_mostrare),
        bandi_per_tab=bandi_per_tab,
        ordine_tab=ordine_tab,
    )

    CARTELLA_OUTPUT.mkdir(parents=True, exist_ok=True)
    percorso_output = CARTELLA_OUTPUT / "index.html"
    percorso_output.write_text(html, encoding="utf-8")
    return percorso_output
