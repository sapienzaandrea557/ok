import logging
import os
import asyncio
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
from ocr_engine import OCREngine
from web_bot import AlloggiatiWebBot

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# States for the conversation
CONFIRM_DATA, EDIT_FIELD = range(2)

class AlloggiatiBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.authorized_user = int(os.getenv("AUTHORIZED_USER_ID", 0))
        self.ocr = OCREngine()
        self.web_bot = AlloggiatiWebBot()
        self.temp_guest_data = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message."""
        if update.effective_user.id != self.authorized_user:
            await update.message.reply_text("Accesso negato. Utente non autorizzato.")
            return
        
        await update.message.reply_text(
            "Benvenuto nel bot per Alloggiati Web! Mandami una foto del documento dell'ospite o il PDF della tabella delle chiavi."
        )

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gestisce l'invio di PDF o immagini (Tabella Chiavi)."""
        if update.effective_user.id != self.authorized_user:
            return

        doc = update.message.document
        file_name = doc.file_name.lower()
        
        if any(x in file_name for x in ["chiav", "tabella"]):
            await update.message.reply_text("Ricevuta tabella delle chiavi! La sto analizzando...")
            
            new_file = await doc.get_file()
            ext = ".pdf" if file_name.endswith(".pdf") else ".jpg"
            temp_path = f"keys_{update.effective_user.id}{ext}"
            await new_file.download_to_drive(temp_path)
            
            try:
                process_path = temp_path
                if temp_path.endswith(".pdf"):
                    process_path = self.ocr.convert_pdf_to_image(temp_path)
                
                keys_data = self.ocr.parse_security_table(process_path)
                with open("security_keys.json", "w") as f:
                    json.dump(keys_data, f)
                
                await update.message.reply_text("Tabella salvata correttamente! Ora posso accedere al portale autonomamente. ✅")
            except Exception as e:
                logging.error(f"Errore tabella: {e}")
                await update.message.reply_text(f"Errore nella lettura della tabella: {e}")
            finally:
                if os.path.exists(temp_path): os.remove(temp_path)
                if 'process_path' in locals() and process_path != temp_path and os.path.exists(process_path):
                    os.remove(process_path)
        else:
            await update.message.reply_text("Documento non riconosciuto. Per la tabella chiavi, il nome deve contenere 'chiavi'.")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Download photo and process with OCR."""
        if update.effective_user.id != self.authorized_user:
            return

        await update.message.reply_text("Ricevuta! Sto estraendo i dati...")
        
        photo_file = await update.message.photo[-1].get_file()
        file_path = f"temp_{update.effective_user.id}.jpg"
        await photo_file.download_to_drive(file_path)

        try:
            ocr_results = self.ocr.extract_text(file_path)
            self.temp_guest_data = self.ocr.parse_guest_data(ocr_results)
            
            msg = "Dati estratti:\n"
            for k, v in self.temp_guest_data.items():
                msg += f"- {k.capitalize()}: {v}\n"
            
            msg += "\nI dati sono corretti? Digita /invia o clicca Modifica."
            keyboard = [['Conferma /invia', 'Modifica']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(msg, reply_markup=reply_markup)
            return CONFIRM_DATA
        except Exception as e:
            logging.error(f"Errore OCR: {e}")
            await update.message.reply_text("Errore nella lettura. Riprova con una foto più nitida.")
        finally:
            if os.path.exists(file_path): os.remove(file_path)

    async def send_to_portal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Inviando i dati al portale Alloggiati Web... 🚀", reply_markup=ReplyKeyboardRemove())
        try:
            await self.web_bot.process_submission(self.temp_guest_data)
            await update.message.reply_text("Dati inviati con successo! ✅")
        except Exception as e:
            logging.error(f"Errore invio: {e}")
            await update.message.reply_text(f"Errore durante l'invio: {e} ❌")
        return ConversationHandler.END

    async def request_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [[k.capitalize()] for k in self.temp_guest_data.keys()]
        keyboard.append(['Annulla'])
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Quale campo vuoi modificare?", reply_markup=reply_markup)
        return EDIT_FIELD

    async def save_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        field = update.message.text.lower()
        if field == 'annulla': return await self.cancel(update, context)
        context.user_data['edit_field'] = field
        await update.message.reply_text(f"Inserisci il nuovo valore per {field}:", reply_markup=ReplyKeyboardRemove())
        return EDIT_FIELD

    async def apply_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        field = context.user_data.get('edit_field')
        new_value = update.message.text.upper()
        if 'date' in field: new_value = new_value.replace(".", "/").replace("-", "/")
        self.temp_guest_data[field] = new_value
        
        msg = "Dati aggiornati:\n"
        for k, v in self.temp_guest_data.items():
            msg += f"- {k.capitalize()}: {v}\n"
        
        msg += "\nCorretto? /invia o Modifica."
        keyboard = [['Conferma /invia', 'Modifica']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(msg, reply_markup=reply_markup)
        return CONFIRM_DATA

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Operazione annullata.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def run(self):
        while True:
            try:
                app = ApplicationBuilder().token(self.token).build()
                conv_handler = ConversationHandler(
                    entry_points=[
                        MessageHandler(filters.PHOTO, self.handle_photo),
                        MessageHandler(filters.Document.ALL, self.handle_document)
                    ],
                    states={
                        CONFIRM_DATA: [
                            CommandHandler("invia", self.send_to_portal),
                            MessageHandler(filters.Regex("^Conferma /invia$"), self.send_to_portal),
                            MessageHandler(filters.Regex("^Modifica$"), self.request_edit),
                        ],
                        EDIT_FIELD: [
                            MessageHandler(filters.TEXT & ~filters.COMMAND, self.apply_edit),
                        ]
                    },
                    fallbacks=[CommandHandler("cancel", self.cancel)],
                )
                app.add_handler(CommandHandler("start", self.start))
                app.add_handler(conv_handler)
                print("Bot is running...")
                app.run_polling(drop_pending_updates=True)
            except Exception as e:
                logging.error(f"Errore bot: {e}. Riavvio...")
                import time
                time.sleep(5)

if __name__ == "__main__":
    bot = AlloggiatiBot()
    bot.run()
