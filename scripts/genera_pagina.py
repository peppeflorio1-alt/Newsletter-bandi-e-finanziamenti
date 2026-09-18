# -*- coding: utf-8 -*-
"""
genera_pagina.py
----------------
Prende la lista finale di bandi e produce il file docs/index.html,
la pagina che GitHub Pages pubblica online.
"""

from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

CARTELLA_TEMPLATE = Path(__file__).resolve().parent.parent / "templates"
CARTELLA_OUTPUT = Path(__file__).resolve().parent.parent / "docs"

ORDINE_LIVELLI = ["comune", "regione", "italia", "europa", "internazionale"]
ETICHETTE_LIVELLI = {
    "comune": "Comuni",
    "regione": "Regioni (Emilia-Romagna, Lombardia, Piemonte, ...)",
    "italia": "Italia",
    "europa": "Europa",
    "internazionale": "Organismi internazionali",
}


def genera(bandi: list[dict], titolo_pagina: str) -> Path:
    """
    Raggruppa i bandi per livello, ordina per data e scrive docs/index.html.
    Ritorna il percorso del file scritto.
    """
    bandi_per_livello: dict[str, list[dict]] = {}
    for bando in bandi:
        bandi_per_livello.setdefault(bando["livello"], []).append(bando)

    for livello in bandi_per_livello:
        bandi_per_livello[livello].sort(
            key=lambda b: (not b.get("nuovo_oggi"), b.get("primo_avvistamento", "")),
            reverse=False,
        )
        # I "nuovi oggi" (False non nuovo -> ordina prima i nuovi) e poi i piu' recenti
        bandi_per_livello[livello].sort(
            key=lambda b: (b.get("nuovo_oggi", False), b.get("primo_avvistamento", "")),
            reverse=True,
        )

    ambiente = Environment(loader=FileSystemLoader(str(CARTELLA_TEMPLATE)))
    modello = ambiente.get_template("pagina.html.jinja")

    html = modello.render(
        titolo_pagina=titolo_pagina,
        data_aggiornamento=datetime.now().strftime("%d/%m/%Y %H:%M"),
        numero_totale_bandi=len(bandi),
        bandi_per_livello=bandi_per_livello,
        ordine_livelli=ORDINE_LIVELLI,
        etichette_livelli=ETICHETTE_LIVELLI,
    )

    CARTELLA_OUTPUT.mkdir(parents=True, exist_ok=True)
    percorso_output = CARTELLA_OUTPUT / "index.html"
    percorso_output.write_text(html, encoding="utf-8")
    return percorso_output
