# Newsletter Bandi — guida per chi parte da zero

Questo progetto legge automaticamente ogni giorno una lista di siti (Comuni,
Regioni, Italia, Europa) alla ricerca di bandi e finanziamenti su cultura,
partecipazione, democrazia e ristrutturazione di spazi/sale eventi, e
pubblica il risultato su una pagina web che aggiorni... senza fare nulla.

Non serve saper programmare per usarlo. Serve solo seguire questi passi
UNA VOLTA per attivarlo. Da quel momento gira da solo, ogni giorno.

---

## 0. Come funziona, in due frasi

- Ogni giorno, un "robot" gratuito di GitHub (si chiama **GitHub Actions**)
  apre questo progetto, esegue lo script Python, legge i siti elencati in
  `config/sources.yaml`, tiene solo i bandi che contengono le tue parole
  chiave, e scrive una pagina web aggiornata dentro la cartella `docs/`.
- **GitHub Pages** (un altro servizio gratuito di GitHub) pubblica quella
  cartella come sito web, con un indirizzo tipo:
  `https://TUONOME.github.io/bandi-newsletter/`

Tu, ogni giorno, apri semplicemente quell'indirizzo. Tutto il resto è
automatico.

---

## 1. Crea un account GitHub (5 minuti, se non lo hai già)

1. Vai su https://github.com e clicca "Sign up".
2. Scegli un nome utente, email, password. È gratis.

## 2. Crea il repository (il "progetto" su GitHub)

1. Una volta loggato, clicca il "+" in alto a destra → "New repository".
2. Nome: `bandi-newsletter` (o quello che preferisci).
3. Visibilità: puoi lasciarlo **Public** (serve per usare GitHub Pages
   gratis) oppure Private se hai un account GitHub Pro/Team.
4. Clicca "Create repository". Lascialo vuoto, senza README: lo carichiamo noi.

## 3. Carica i file di questo progetto nel repository

Il modo più semplice, senza usare la riga di comando:

1. Nella pagina del tuo nuovo repository, clicca "uploading an existing file"
   (o "Add file" → "Upload files").
2. Trascina dentro TUTTI i file e le cartelle che trovi in questo progetto
   (mantenendo la struttura: `config/`, `scripts/`, `templates/`, `data/`,
   `docs/`, `.github/`, `requirements.txt`, `README.md`).
   - Nota: le cartelle che iniziano con il punto (come `.github`) a volte
     l'interfaccia web di GitHub le nasconde durante il trascinamento.
     Se succede, è più affidabile usare **GitHub Desktop** (punto 3-bis
     sotto) invece del caricamento da browser.
3. Scrivi un messaggio tipo "Primo caricamento" e clicca "Commit changes".

### 3-bis. Alternativa più affidabile: GitHub Desktop (consigliata)

1. Scarica e installa **GitHub Desktop**: https://desktop.github.com
   (ha un'interfaccia grafica, nessuna riga di comando).
2. Accedi con il tuo account GitHub.
3. "File" → "Clone repository" → scegli il repository `bandi-newsletter`
   che hai appena creato → scegli dove salvarlo sul tuo computer.
4. Copia dentro quella cartella tutti i file di questo progetto.
5. Torna su GitHub Desktop: vedrai la lista dei file aggiunti.
   Scrivi un messaggio (es. "Primo caricamento") e clicca "Commit to main",
   poi "Push origin" in alto a destra.

## 4. Attiva GitHub Pages

1. Nel tuo repository su github.com, vai su "Settings" (in alto).
2. Nel menu a sinistra clicca "Pages".
3. Sotto "Build and deployment" → "Source", scegli "Deploy from a branch".
4. Sotto "Branch", scegli `main` e la cartella `/docs`. Clicca "Save".
5. Dopo un paio di minuti, GitHub ti mostrerà l'indirizzo della tua pagina
   (tipo `https://TUONOME.github.io/bandi-newsletter/`). Salvalo nei preferiti.

## 4-bis. Una nota su "aggiornare quando voglio io"

Su tua richiesta, la newsletter **non si aggiorna piu' da sola ogni giorno**:
si aggiorna solo quando tu lo decidi, dal tab "Actions" (vedi punto 5).

Una precisazione onesta: non e' possibile mettere un pulsante "Aggiorna"
direttamente sulla pagina pubblicata (quella su GitHub Pages) che avvii lo
script. Il motivo e' di sicurezza: far partire lo script richiede una
"chiave" di accesso al tuo repository, e se quella chiave fosse scritta
dentro la pagina pubblica, chiunque visitasse il sito potrebbe rubarla e
modificare il tuo repository. Per questo l'aggiornamento manuale si fa dal
tab "Actions" di GitHub (che vedi solo tu, da loggato).

Per renderlo il piu' comodo possibile, salva nei preferiti anche questo
indirizzo (sostituendo TUONOME): si apre gia' sulla pagina giusta, cosi'
ti serve un solo click in piu' per lanciare l'aggiornamento:

```
https://github.com/TUONOME/bandi-newsletter/actions/workflows/daily.yml
```

## 5. Avvia il primo aggiornamento

1. Vai sul tab "Actions" del tuo repository.
2. Se è la prima volta, GitHub potrebbe chiederti di confermare che vuoi
   abilitare i workflow: clicca "I understand my workflows, go ahead and
   enable them".
3. Nella lista a sinistra, clicca "Aggiorna newsletter bandi ogni giorno".
4. Clicca il pulsante "Run workflow" (in alto a destra) → "Run workflow".
5. Aspetta 1-2 minuti, aggiorna la pagina: dovresti vedere un segno di
   spunta verde. Significa che è andato tutto bene.
6. Apri l'indirizzo di GitHub Pages del punto 4: dovresti vedere la pagina
   con i bandi trovati.

**Da qui in poi, tutto è automatico**: ogni giorno alle 06:00 UTC il
workflow si ripete da solo e la pagina si aggiorna.

---

## 5-bis. Il catalogo delle 100 fonti che hai raccolto tu

Il file `config/fonti_da_configurare.yaml` contiene le 100 fonti che hai
individuato (Unione Europea, ministeri, le tre Regioni, fondazioni bancarie,
portali del Terzo Settore, bandi settoriali). **Lo script NON legge questo
file**: è una lista di partenza, un "magazzino" di indirizzi. Nessuno di
questi 100 indirizzi è stato verificato (io non ho potuto controllarli con
un browser): sono i siti di partenza da cui cercare la vera pagina bandi
o il feed RSS.

Il flusso di lavoro consigliato è:

1. Scegli una fonte da `fonti_da_configurare.yaml` (magari cominciando dalle
   tre Regioni e dal Funding & Tenders Portal, visto che sono la tua
   priorità).
2. Segui il paragrafo 6 qui sotto per trovare il feed RSS o i selettori HTML.
3. Aggiungi la fonte a `config/sources.yaml` (quello vero, letto dallo
   script), con `url` completo e, se serve, `selettori`.
4. Facoltativo: cancella quella voce da `fonti_da_configurare.yaml` per
   tenere traccia di cosa hai già attivato (non è obbligatorio, è solo per
   ordine).

Non c'è fretta né un ordine obbligato: puoi attivarne una alla volta, anche
una alla settimana, e la newsletter funziona comunque con quelle già attive.

---

## 6. Cosa fare se un sito non ha ancora dei risultati corretti

Ti avviso subito: gli URL scritti in `config/sources.yaml` sono **esempi
plausibili ma non verificati** (chi ha preparato questo progetto non aveva
accesso a internet per controllarli sito per sito). Alcuni potrebbero non
funzionare finché non li correggi. Ecco come fare, senza programmare:

### Caso A — Il sito ha un feed RSS (il caso più semplice)

Molti siti di enti pubblici hanno un feed RSS per la sezione bandi/avvisi.
Per trovarlo:
1. Vai sulla pagina "Bandi" o "Avvisi" del sito che ti interessa.
2. Cerca un'iconcina arancione, o un link con scritto "RSS", spesso in fondo
   alla pagina o nel footer del sito.
3. Se non lo trovi visivamente, prova ad aggiungere `/feed`, `/rss` o
   `?format=feed` alla fine dell'indirizzo della pagina bandi, oppure cerca
   su Google: `site:nomesito.it rss bandi`.
4. Una volta trovato l'indirizzo del feed, apri `config/sources.yaml` e
   incolla quell'indirizzo al posto di quello sbagliato, nel campo `url:`
   della fonte corrispondente. Togli anche la riga `da_verificare: true`
   quando hai controllato che funziona.

### Caso B — Il sito NON ha un feed RSS (serve leggere la pagina HTML)

Questo richiede un piccolo sforzo in più (5-10 minuti), ma niente codice:

1. Apri la pagina bandi del sito nel browser (Chrome o Firefox).
2. Fai clic destro su uno dei bandi elencati → "Ispeziona" (o "Ispeziona
   elemento"). Si apre un pannello con il codice della pagina.
3. Nel pannello, muovi il mouse sulle righe di codice: la pagina evidenzia
   in blu la parte corrispondente. Cerca l'elemento che "contiene" un
   singolo bando (di solito un `<div>` o `<article>` che si ripete per ogni
   bando nella lista).
4. Prendi nota del suo "selettore": di solito basta il nome della classe,
   es. se vedi `<article class="risultato-bando">`, il selettore è
   `article.risultato-bando`.
5. Dentro quell'elemento, trova il titolo (di solito dentro un `<a>` o
   `<h2>/<h3>`) e nota anche il suo selettore.
6. Apri `config/sources.yaml`, e per quella fonte scrivi `tipo: html` e
   compila la sezione `selettori:` seguendo l'esempio già presente nel file
   (quello del "Comune di Grazzanise").
7. Se vuoi che compaia anche la **data di scadenza**, ripeti lo stesso
   procedimento cercando l'elemento che la mostra (spesso vicino a scritte
   come "Scade il", "Chiude il", "Termine per la presentazione delle
   domande"): aggiungi `scadenza: "il-suo-selettore"` sotto `selettori:`.
   A volte la data e' scritta in un campo nascosto della pagina invece che
   nel testo visibile (e' il caso della Regione Lombardia, gia'
   configurata): se vedi un tag `<input ... value="2026-10-21">`, usa
   `scadenza: "il-selettore-di-quell-input"` insieme a
   `scadenza_attributo: "value"`.

Se questo passaggio ti sembra troppo tecnico, puoi anche semplicemente:
- mandarmi (a me, Claude, in una prossima conversazione) uno screenshot o
  il link della pagina bandi che vuoi aggiungere, e ti preparo io la riga
  di configurazione esatta da incollare.

### Caso C-bis — Il sito usa Plone (molto comune per Regioni/Comuni)

Alcuni siti pubblici italiani (tra cui Regione Emilia-Romagna, gia' attivata
in questo progetto) sono costruiti con una piattaforma chiamata **Plone**
e offrono i dati anche in JSON, molto piu' affidabile dell'HTML. Il segnale
per riconoscerla: apri gli strumenti sviluppatore del browser (F12) ->
scheda "Rete"/"Network", ricarica la pagina bandi, e cerca richieste con
`++api++` nell'indirizzo. Se ci sono, usa `tipo: plone` invece di `html` —
i dettagli su come scrivere la fonte sono spiegati all'inizio del file
`scripts/fetch_plone.py`. In una prossima conversazione posso anche
verificarlo io per te, se mi dai il link della pagina.

### Caso C — Un sito blocca le richieste automatiche

Alcuni siti pubblici hanno protezioni anti-robot piuttosto aggressive
(es. Cloudflare). Se una fonte continua a dare errore anche con
l'indirizzo giusto, è probabile che il sito blocchi le richieste
automatiche: in quel caso quella fonte va tenuta d'occhio manualmente,
oppure sostituita con la newsletter ufficiale del sito, se esiste.

---

## 7. Come modificare le parole chiave o aggiungere/togliere una fonte

Tutto si fa in **un solo file**: `config/sources.yaml`.

- Per aggiungere una parola chiave: apri il file su GitHub (clicca sul file,
  poi sulla matita in alto a destra per modificarlo), vai alla sezione
  `parole_chiave:` e aggiungi una riga con un trattino, es.:
  ```yaml
  parole_chiave:
    - cultura
    - la_tua_nuova_parola
  ```
- Per aggiungere una fonte: copia un blocco esistente sotto `fonti:` e
  cambia `nome`, `livello`, `url` (e `selettori` se è di tipo `html`).
- Per togliere una fonte o parola: cancella semplicemente la riga o il
  blocco corrispondente.
- Dopo aver modificato, clicca "Commit changes" in fondo alla pagina di
  modifica di GitHub. Al prossimo aggiornamento automatico (o lanciandolo
  a mano dal tab "Actions", vedi punto 5), la modifica sarà attiva.

Non serve toccare nessun altro file per queste modifiche.

---

## 8. Provare il progetto sul proprio computer (facoltativo)

Se in futuro vuoi installare Python sul tuo computer e provare il progetto
in locale prima di caricarlo su GitHub:

1. Installa Python (versione 3.11 o superiore) da https://www.python.org/downloads/
   Durante l'installazione su Windows, spunta la casella "Add Python to PATH".
2. Apri il "Prompt dei comandi" (Windows) o "Terminale" (Mac), spostati
   nella cartella del progetto e digita:
   ```
   pip install -r requirements.txt
   python scripts/main.py
   ```
3. Il file `docs/index.html` verrà aggiornato: aprilo con doppio clic per
   vederlo nel browser.

Per verificare che tutto il codice funzioni correttamente (usando dati di
prova, senza scaricare nulla da internet):
```
python tests/test_pipeline.py
```
Se vedi scritto "Tutti i test sono passati.", il codice è a posto.

---

## 9. Struttura del progetto (per curiosità, non serve impararla a memoria)

```
bandi-newsletter/
├── config/
│   ├── sources.yaml               <- L'UNICO file letto dallo script
│   └── fonti_da_configurare.yaml  <- Magazzino delle 100 fonti da attivare
├── scripts/
│   ├── main.py              regista: coordina tutto
│   ├── fetch_rss.py         legge le fonti con feed RSS
│   ├── fetch_html.py        legge le fonti senza feed RSS (pagine HTML)
│   ├── filters.py           applica le parole chiave
│   ├── stato.py             ricorda i bandi già visti tra un giorno e l'altro
│   └── genera_pagina.py     scrive la pagina web finale
├── templates/
│   └── pagina.html.jinja    l'aspetto grafico della pagina
├── data/
│   └── stato.json           "memoria" del progetto (creato/aggiornato da solo)
├── docs/
│   └── index.html           la pagina pubblicata da GitHub Pages
├── tests/
│   └── test_pipeline.py     test con dati finti, per controllare che nulla si sia rotto
├── .github/workflows/
│   └── daily.yml             dice a GitHub Actions cosa fare ogni giorno
└── requirements.txt          elenco delle librerie Python necessarie
```

---

## 10. Domande frequenti

**"Il sito EU Funding & Tenders Portal è nella lista?"**
No, è stato lasciato solo commentato in `config/sources.yaml` come
promemoria: il portale UE cambia spesso struttura tecnica e non potevo
verificarlo. Se vuoi, in una prossima conversazione possiamo configurarlo
insieme controllando la pagina reale.

**"Posso ricevere anche un'email, oltre alla pagina web?"**
Sì, è possibile aggiungerlo in un secondo momento (es. con un servizio
gratuito come SendGrid o semplicemente Gmail via SMTP): lo lasciamo fuori
ora per mantenere il progetto semplice, ma la struttura del codice lo
permette senza riscrivere nulla.

**"Quanti giorni resta visibile un bando nella pagina?"**
Per default 60 giorni dall'ultima volta che è stato trovato sul sito di
origine. Si cambia nel campo `giorni_di_permanenza` di `config/sources.yaml`.

**"Cosa succede se sbaglio qualcosa nel file di configurazione?"**
Il peggio che può succedere è che lo script si accorga dell'errore e lo
segnali nel tab "Actions" (segno rosso invece che verde) senza cambiare la
pagina pubblicata. Non puoi "rompere" nulla in modo permanente: puoi sempre
tornare alla versione precedente di un file su GitHub (ogni file ha uno
storico delle modifiche, sotto "History").
