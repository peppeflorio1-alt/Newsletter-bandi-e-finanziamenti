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


def tab_di(voce: dict) -> str:
    """Decide in quale tab finisce una 'voce' (un bando, ma anche una
    fonte configurata): una tab per ogni area/regione (i bandi/le fonti di
    un Comune finiscono nella tab della loro stessa regione), altrimenti
    Italia / Europa / Internazionale in base al livello."""
    if voce["livello"] in ("regione", "comune") and voce.get("area"):
        return voce["area"]
    if voce["livello"] == "italia":
        return "Italia"
    if voce["livello"] == "europa":
        return "Europa"
    if voce["livello"] == "internazionale":
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


def genera(bandi: list[dict], titolo_pagina: str, chiavi_monitorate: set[str] | None = None) -> Path:
    """
    Tiene solo i bandi aperti o di prossima apertura, li raggruppa in tab
    e scrive docs/index.html. Ritorna il percorso del file scritto.

    'chiavi_monitorate' e' l'insieme delle tab per cui esiste almeno una
    fonte configurata (calcolato da main.py a partire da sources.yaml):
    serve per mostrare comunque quella tab, con un messaggio, anche nei
    giorni in cui non ha bandi aperti da mostrare - cosi' si vede che la
    fonte viene controllata regolarmente, invece di far sparire la tab.
    """
    chiavi_monitorate = chiavi_monitorate or set()

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
        bandi_per_tab.setdefault(tab_di(bando), []).append(bando)

    for chiave in bandi_per_tab:
        bandi_per_tab[chiave].sort(
            key=lambda b: (b.get("nuovo_oggi", False), b.get("primo_avvistamento", "")),
            reverse=True,
        )

    # Aggiunge (vuote) le tab monitorate che oggi non hanno bandi da mostrare,
    # cosi' compaiono comunque con un messaggio invece di sparire.
    for chiave in chiavi_monitorate:
        bandi_per_tab.setdefault(chiave, [])

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
