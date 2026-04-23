import json
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class AlloggiatiWebBot:
    def __init__(self):
        self.url = "https://alloggiatiweb.poliziadistato.it/AlloggiatiWeb/"
        self.username = os.getenv("ALLOGGIATI_USERNAME")
        self.password = os.getenv("ALLOGGIATI_PASSWORD")
        self.cert_path = os.getenv("ALLOGGIATI_CERT_PATH")
        self.cert_pass = os.getenv("ALLOGGIATI_CERT_PASS")
        self.struttura_id = os.getenv("STRUTTURA_ID")
        self.keys_file = "security_keys.json"

    def load_security_keys(self):
        """Carica la tabella delle chiavi dal file JSON."""
        if os.path.exists(self.keys_file):
            with open(self.keys_file, 'r') as f:
                return json.load(f)
        return None

    async def handle_security_challenge(self, page):
        """Gestisce la richiesta dei numeri dalla tabella delle chiavi."""
        keys = self.load_security_keys()
        if not keys:
            print("ERRORE: Tabella delle chiavi non trovata! Mandami il PDF o la foto su Telegram.")
            return False

        # Il portale chiede solitamente 4 numeri, es: "Sezione 2, Numero 1"
        # Cerchiamo le etichette nel testo della pagina
        try:
            challenge_text = await page.content()
            # Esempio di ricerca: "posizione 2 della sezione 1"
            # Questa parte va raffinata con i selettori reali
            prompts = await page.query_selector_all("label[for*='txtChiave']")
            
            for i, prompt in enumerate(prompts):
                text = await prompt.inner_text()
                # Esempio testo: "Inserire il numero alla posizione 3 della sezione 2"
                match = re.search(r'posizione (\d+) della sezione (\d+)', text)
                if match:
                    pos, sez = match.groups()
                    key_value = keys.get(sez, {}).get(pos)
                    if key_value:
                        await page.fill(f"#txtChiave{i+1}", key_value)
            
            await page.click("#btnConfermaChiavi")
            return True
        except Exception as e:
            print(f"Errore nella sfida di sicurezza: {e}")
            return False

    async def login(self, page):
        """Log in to the portal with detailed logging and retry logic."""
        try:
            print(f"Tentativo di accesso a {self.url}...")
            await page.goto(self.url, wait_until="networkidle", timeout=60000)
            
            # Controllo se siamo già loggati o se serve il certificato
            if "Certificato Digitale" in await page.content():
                print("Il portale richiede la selezione del certificato...")
                # In molti casi con Playwright, se il certificato è nel context, 
                # il browser lo presenta automaticamente o appare un popup di sistema.
            
            # Esempio di riempimento campi (da adattare con i selettori reali del portale)
            # Questi selettori cambiano spesso, quindi usiamo logiche di ricerca testo
            try:
                await page.get_by_label("Utente").fill(self.username)
                await page.get_by_label("Password").fill(self.password)
                await page.get_by_role("button", name="Accedi").click()
            except Exception as e:
                print(f"Selettori standard non trovati, provo ricerca generica: {e}")
                # Fallback su selettori comuni
                await page.fill("input[name*='utente']", self.username)
                await page.fill("input[name*='pass']", self.password)
                await page.click("button[type='submit'], input[type='submit']")

            await page.wait_for_load_state("networkidle")
            
            # GESTIONE SFIDA SICUREZZA (Tabella Chiavi)
            if "Inserire i numeri" in await page.content() or "posizione" in await page.content():
                print("Sfida di sicurezza rilevata. Inserimento codici dalla tabella...")
                success = await self.handle_security_challenge(page)
                if not success:
                    raise Exception("Impossibile superare la sfida di sicurezza. Controlla la tabella chiavi.")

            print("Login completato o in attesa di dashboard.")
            
        except Exception as e:
            print(f"Errore critico durante il login: {e}")
            await page.screenshot(path="login_error.png") # Salva prova dell'errore
            raise

    async def enter_guest_data(self, page, guest_data):
        """Fill the guest form with real selectors (based on typical portal structure)."""
        print(f"Inserimento dati per {guest_data['name']} {guest_data['surname']}...")
        
        try:
            # 1. Navigazione verso Inserimento Online
            await page.get_by_role("link", name="Inserimento Online").click()
            await page.get_by_role("link", name="Inserimento Singolo").click()
            
            # 2. Selezione tipo alloggiato (Ospite Singolo di default)
            await page.select_option("select[name*='TipoAlloggiato']", value="16") # 16 è solitamente Ospite Singolo
            
            # 3. Dati anagrafici
            await page.fill("input[name*='Cognome']", guest_data['surname'])
            await page.fill("input[name*='Nome']", guest_data['name'])
            await page.fill("input[name*='DataNascita']", guest_data['birth_date'])
            
            # Sesso (M/F) - Heuristic: se finisce per 'A' probabile F, altrimenti M
            sesso = "F" if guest_data['name'].endswith('A') else "M"
            await page.select_option("select[name*='Sesso']", value=sesso)
            
            # 4. Cittadinanza e Luogo di Nascita
            # Nota: Questi campi spesso usano degli autocomplete o codici ISTAT
            await page.fill("input[name*='Cittadinanza']", guest_data['nationality'])
            await page.press("input[name*='Cittadinanza']", "Enter")
            
            # 5. Documento
            doc_map = {
                "CARTA_IDENTITA": "IDENT", # Codici comuni
                "PASSAPORTO": "PASSA",
                "PATENTE": "PATEN"
            }
            doc_type_code = doc_map.get(guest_data['doc_type'], "IDENT")
            await page.select_option("select[name*='TipoDocumento']", value=doc_type_code)
            await page.fill("input[name*='NumeroDocumento']", guest_data['doc_number'])
            
            # 6. Luogo di rilascio
            await page.fill("input[name*='LuogoRilascio']", "ITALIA") # Default
            
            # 7. INVIO
            # Inizialmente commentato per sicurezza, l'utente deve confermare nel bot
            # await page.click("button[id*='btnInvia']")
            
            print("Modulo compilato correttamente.")
            
        except Exception as e:
            print(f"Errore durante l'inserimento dati: {e}")
            await page.screenshot(path="form_error.png")
            raise

    async def process_submission(self, guest_data):
        """Main entry point for web automation."""
        async with async_playwright() as p:
            # Configurazione certificato se presente
            context_args = {}
            if self.cert_path and os.path.exists(self.cert_path):
                # Playwright supporta certificati client tramite l'argomento 'client_certificates'
                # Nota: il percorso deve essere assoluto
                abs_cert_path = os.path.abspath(self.cert_path)
                context_args["client_certificates"] = [{
                    "origin": "https://alloggiatiweb.poliziadistato.it",
                    "certPath": abs_cert_path,
                    "password": self.cert_pass
                }]
            
            browser = await p.chromium.launch(headless=True) # Metti False per vedere cosa succede
            context = await browser.new_context(**context_args)
            page = await context.new_page()
            
            try:
                await self.login(page)
                await self.enter_guest_data(page, guest_data)
            finally:
                await browser.close()

if __name__ == "__main__":
    # Test stub
    # bot = AlloggiatiWebBot()
    # asyncio.run(bot.process_submission({"name": "Mario", "surname": "Rossi"}))
    pass
