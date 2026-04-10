# ⚽ Smart Brain AI - Football Predictor PRO

Benvenuto nel sistema di analisi e predizione calcistica più avanzato per Trae IDE. **Smart Brain AI** non è un semplice calcolatore di probabilità, ma un ecosistema decisionale che combina modelli statistici (Poisson), simulazioni Monte Carlo, analisi del valore matematico (**Expected Value**) e gestione del bankroll (**Criterio di Kelly**).

## 🚀 Funzionalità di Punta

### 1. 🧠 Architettura Decisionale Dinamica
L'IA non sceglie più solo la scommessa "più probabile", ma quella con il miglior rapporto rischio/rendimento:
- **Expected Value (EV)**: Calcola `(Probabilità * Quota) - 1`. Identifica quando i bookmaker stanno sottovalutando un esito.
- **Criterio di Kelly (Frazionario 1/10)**: Suggerisce lo **Stake ottimale** (% del tuo budget) per ogni giocata, proteggendo il capitale dai periodi di varianza negativa.
- **Analisi Multi-Livello**: Fornisce tre opzioni per ogni match: **FACILE** (Alta probabilità), **MEDIA** (Miglior valore/Consigliata), **DIFFICILE** (Alta quota/Valore puro).

### 2. 📡 Sistema di Fallback a 4 Livelli (Anti-Limit)
Per superare i limiti delle API gratuite e coprire tutte le stagioni (2025/2026 incluse):
1. **API-Sports**: Fonte primaria per statistiche pro e xG.
2. **Football-Data.org**: Fallback per i campionati principali europei.
3. **ESPN Scoreboard**: Recupero in tempo reale di calendari e risultati live/finiti per TUTTI i campionati mondiali.
4. **Local CSV Database**: Integrazione di file `.csv` (Serie A, Premier, etc.) per analisi storiche profonde senza consumare crediti API.

### 3. 📊 Analisi Pro e Mercati Avanzati
Oltre al classico 1X2 e Under/Over, il sistema analizza:
- **Corner, Cartellini, Tiri e Falli**: Calcolo delle probabilità basato sulle medie reali delle squadre.
- **Expected Goals (xG)**: Integra la qualità delle occasioni create per affinare le medie gol previste.
- **Fatica e Infortuni**: Considera i giorni di riposo dall'ultimo match e l'impatto delle assenze chiave.

### 4. 📈 Auto-Learning & Analisi Storica (Opzione 11)
- **Addestramento Continuo**: L'IA impara dai propri errori aggiornando i pesi in `weights.json` dopo ogni verifica dei risultati.
- **Analisi Retroattiva**: Con l'Opzione 11 puoi analizzare interi giorni passati per "allenare" velocemente il cervello dell'IA sui dati recenti.

### 5. ✅ Reality Mode (Opzione 10) - RISOLTO IL BUG 'PENDING'
La Modalità Realtà è stata completamente riscritta:
- **Matching Elastico**: Riconosce i team anche con nomi diversi tra le fonti (es. "Inter" vs "Internazionale").
- **Persistenza Risultati**: Una volta che un risultato viene trovato su ESPN o API, viene salvato permanentemente in `history.json`. **Niente più match bloccati in PENDING**.
- **Confronto Live**: Mostra l'esito dei pronostici in tempo reale durante lo svolgimento delle partite.

## 📂 File Chiave

- [si.py](file:///c:/Users/pc\Desktop\calcio\si.py): Il motore principale dell'IA e l'interfaccia utente.
- [weights.json](file:///c:/Users/pc\Desktop\calcio\weights.json): I parametri di intelligenza del modello (Forma, Classifica, H2H, Contesto).
- [history.json](file:///c:/Users/pc\Desktop\calcio\history.json): Il database dei pronostici e dei risultati reali per l'apprendimento.
- [api_cache.json](file:///c:/Users/pc\Desktop\calcio\api_cache.json): Cache per massimizzare l'efficienza delle API Key.

## 🛠️ Guida Rapida

1. **Analisi Giornaliera**: Usa l'Opzione **9 (LISTA)** per scegliere i match di oggi/domani.
2. **Verifica Esiti**: Usa l'Opzione **10 (REALTA)** per vedere cosa hai preso e cosa no.
3. **Addestramento**: Usa l'Opzione **11** se vuoi che l'IA studi i risultati dei giorni scorsi per migliorare i futuri pronostici.

---
*Smart Brain AI: La statistica al servizio del profitto.*
