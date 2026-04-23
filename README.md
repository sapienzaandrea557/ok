# Alloggiati Web Automator 🚀

Questo progetto è un sistema **100% autonomo** progettato per gestire le comunicazioni obbligatorie al portale **Alloggiati Web (Polizia di Stato)** per case vacanze e strutture ricettive. 

Il sistema permette di inviare i dati degli ospiti semplicemente scattando una foto al loro documento d'identità tramite un Bot Telegram privato.

---

## 🌟 Funzionalità Principali

- **OCR Avanzato (EasyOCR)**: Estrazione automatica dei dati da Carte d'Identità Elettroniche (CIE), Passaporti e Patenti italiane.
- **Supporto MRZ**: Lettura della "Machine Readable Zone" per la massima precisione sui dati sensibili.
- **Automazione Web (Playwright)**: Inserimento automatico dei dati sul portale Alloggiati Web, navigando il sito come un vero utente.
- **Gestione 2FA (Tabella delle Chiavi)**: Superamento automatico della sfida di sicurezza del portale tramite il caricamento preventivo della matrice dei numeri.
- **Bot Telegram Privato**: Interfaccia semplice e sicura. Solo l'utente autorizzato (ID: `7168811709`) può interagire con il sistema.
- **Correzione Manuale**: Possibilità di modificare i dati estratti direttamente dalla chat di Telegram prima dell'invio definitivo.
- **Auto-Riavvio**: Sistema di monitoraggio che riavvia il bot in caso di errori di rete o crash.

---

## 🛠️ Struttura del Progetto

- **`main.py`**: Il cuore del sistema che gestisce la comunicazione con Telegram e coordina gli altri moduli.
- **`ocr_engine.py`**: Motore di riconoscimento ottico dei caratteri, configurato per documenti italiani e internazionali.
- **`web_bot.py`**: Modulo di automazione web che gestisce il login (inclusa la tabella chiavi) e l'inserimento delle schedine.
- **`requirements.txt`**: Elenco di tutte le librerie Python necessarie.
- **`.env`**: File di configurazione per credenziali e token (da non condividere!).

---

## 🚀 Guida all'Installazione

### 1. Prerequisiti
Assicurati di avere Python 3.8+ installato sul tuo sistema.

### 2. Installazione Dipendenze
Apri il terminale nella cartella del progetto ed esegui:
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configurazione
Rinomina il file `.env.example` in `.env` (se non l'hai già fatto) e compila i seguenti campi:
- `ALLOGGIATI_USERNAME`: La tua username del portale.
- `ALLOGGIATI_PASSWORD`: La tua password del portale.
- `STRUTTURA_ID`: Il codice della tua struttura.
- `TELEGRAM_BOT_TOKEN`: Il token ottenuto da [@BotFather](https://t.me/botfather).
- `AUTHORIZED_USER_ID`: Il tuo ID Telegram (già impostato su `7168811709`).

### 4. Avvio
Esegui lo script principale:
```bash
python main.py
```

---

## 📖 Come si usa

1. **Configurazione Iniziale**: Avvia il bot e manda il PDF o la foto della tua **Tabella delle Chiavi**. Il bot la salverà e non dovrai più mandarla.
2. **Registrazione Ospite**: Scatta una foto nitida al documento dell'ospite e inviala al bot.
3. **Verifica**: Controlla i dati estratti dal bot. Se sono corretti, premi **Conferma /invia**.
4. **Fatto!**: Il bot effettuerà il login, supererà la sfida di sicurezza e registrerà l'ospite per te.

---

## 🛡️ Sicurezza e Privacy

- **Dati Locali**: Le foto dei documenti vengono cancellate immediatamente dopo l'elaborazione.
- **Accesso Esclusivo**: Solo il tuo ID Telegram può comandare il bot. Messaggi da altri utenti verranno ignorati.
- **Certificati**: Supporto completo per l'accesso tramite certificato digitale `.pfx` se richiesto dalla tua Questura.

---

## 🧪 Test di Simulazione
Puoi verificare che tutto sia configurato correttamente eseguendo:
```bash
python dry_run_test.py
```
Questo simulerà un intero ciclo di lavoro senza inviare dati reali al portale.

---

**Sviluppato con ❤️ per semplificare la vita degli host.**
