# -*- coding: utf-8 -*-
"""
main.py
-------
Questo e' lo script "regista": legge la configurazione, chiama i vari
moduli in ordine, e alla fine scrive la pagina web aggiornata.

Per lanciarlo a mano (facoltativo, di solito ci pensa GitHub Actions):

    python scripts/main.py

Non serve modificare questo file per usare il progetto: per aggiungere o
togliere fonti/parole chiave si modifica solo config/sources.yaml.
"""

import sys
import yaml
from pathlib import Path

# Permette di lanciare "python scripts/main.py" dalla cartella principale
sys.path.insert(0, str(Path(__file__).resolve().parent))

import fetch_rss
import fetch_html
import fetch_plone
import fetch_wordpress
import filters
import stato
import genera_pagina

PERCORSO_CONFIGURAZIONE = Path(__file__).resolve().parent.parent / "config" / "sources.yaml"


def carica_configurazione() -> dict:
    with open(PERCORSO_CONFIGURAZIONE, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def raccogli_bandi_da_tutte_le_fonti(fonti: list[dict]) -> list[dict]:
    tutti_i_bandi = []
    for fonte in fonti:
        print(f"-> Leggo: {fonte['nome']} ({fonte['tipo']})")
        try:
            if fonte["tipo"] == "rss":
                trovati = fetch_rss.fetch(fonte)
            elif fonte["tipo"] == "html":
                trovati = fetch_html.fetch(fonte)
            elif fonte["tipo"] == "plone":
                trovati = fetch_plone.fetch(fonte)
            elif fonte["tipo"] == "wordpress":
                trovati = fetch_wordpress.fetch(fonte)
            else:
                print(f"[ATTENZIONE] Tipo di fonte sconosciuto '{fonte['tipo']}' per {fonte['nome']}: saltata.")
                continue
        except Exception as errore:
            # Una fonte che fallisce non deve mai bloccare tutte le altre.
            print(f"[ERRORE] Problema con la fonte '{fonte['nome']}': {errore}")
            continue

        print(f"   trovati {len(trovati)} elementi")
        tutti_i_bandi.extend(trovati)
    return tutti_i_bandi


def main():
    configurazione = carica_configurazione()

    fonti_attive = configurazione.get("fonti", [])
    parole_chiave = configurazione.get("parole_chiave", [])
    impostazioni = configurazione.get("impostazioni", {})
    giorni_di_permanenza = impostazioni.get("giorni_di_permanenza", 60)
    titolo_pagina = impostazioni.get("titolo_pagina", "Newsletter bandi")

    print(f"=== Avvio raccolta bandi da {len(fonti_attive)} fonti ===")
    bandi_grezzi = raccogli_bandi_da_tutte_le_fonti(fonti_attive)
    print(f"Totale elementi raccolti (prima del filtro): {len(bandi_grezzi)}")

    bandi_filtrati = filters.filtra_per_parole_chiave(bandi_grezzi, parole_chiave)
    print(f"Totale dopo il filtro per parole chiave: {len(bandi_filtrati)}")

    stato_salvato = stato.carica_stato()
    bandi_da_mostrare = stato.aggiorna_stato_e_arricchisci(bandi_filtrati, stato_salvato, giorni_di_permanenza)
    stato.salva_stato(stato_salvato)
    print(f"Totale bandi da mostrare nella pagina (inclusi quelli dei giorni scorsi): {len(bandi_da_mostrare)}")

    chiavi_monitorate = {genera_pagina.tab_di(fonte) for fonte in fonti_attive}
    percorso_pagina = genera_pagina.genera(bandi_da_mostrare, titolo_pagina, chiavi_monitorate=chiavi_monitorate)
    print(f"=== Fatto. Pagina scritta in: {percorso_pagina} ===")


if __name__ == "__main__":
    main()
