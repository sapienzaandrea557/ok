import easyocr
import cv2
import numpy as np
import re
from PIL import Image
import os
import fitz # PyMuPDF

class OCREngine:
    def __init__(self, languages=['it', 'en']):
        # Initialize the reader
        self.reader = easyocr.Reader(languages, gpu=False)
        print("OCR Engine Initialized")

    def convert_pdf_to_image(self, pdf_path):
        """Converte la prima pagina di un PDF in un'immagine per l'OCR."""
        doc = fitz.open(pdf_path)
        page = doc.load_page(0) # Carica la prima pagina
        pix = page.get_pixmap()
        img_path = pdf_path.replace(".pdf", ".jpg")
        pix.save(img_path)
        doc.close()
        return img_path

    def extract_text(self, image_path):
        """Extract text using EasyOCR."""
        if image_path.lower().endswith(".pdf"):
            image_path = self.convert_pdf_to_image(image_path)
            
        result = self.reader.readtext(image_path)
        return result

    def parse_guest_data(self, ocr_results):
        """
        Extract specific guest fields from OCR results.
        Requires heavy regex matching for Italian ID/Passports.
        """
        full_text = " ".join([res[1] for res in ocr_results]).upper()
        print(f"Full Text Extracted: {full_text}")

        data = {
            "surname": "",
            "name": "",
            "birth_date": "",
            "birth_place": "",
            "nationality": "ITALIANA",
            "doc_type": "CARTA_IDENTITA",
            "doc_number": "",
            "issue_date": "",
            "expiry_date": ""
        }

        # Regex for Dates (DD/MM/YYYY or DD.MM.YYYY or DD-MM-YYYY)
        date_pattern = r'\b(\d{2}[/.-]\d{2}[/.-]\d{4})\b'
        dates = re.findall(date_pattern, full_text)
        
        if len(dates) >= 3:
            # Ordiniamo le date trovate per assicurarci di assegnare bene nascita, rilascio, scadenza
            # La data di nascita è solitamente la più lontana nel passato
            sorted_dates = sorted(dates, key=lambda x: re.sub(r'[/.-]', '', x)[::-1])
            data["birth_date"] = sorted_dates[0]
            data["issue_date"] = sorted_dates[1]
            data["expiry_date"] = sorted_dates[2]
        elif len(dates) == 1:
            data["birth_date"] = dates[0]

        # Regex per documenti italiani (Carta Identità, Passaporto, Patente)
        patterns = {
            "CARTA_IDENTITA": r'\b([A-Z]{2}\d{5}[A-Z]{2})\b', # CIE
            "PASSAPORTO": r'\b([A-Z]\d{7})\b',
            "PATENTE": r'\b([A-Z]{2}\d{7}[A-Z])\b'
        }

        # Ricerca MRZ (Machine Readable Zone) - Estremamente affidabile per Passaporti e CIE
        mrz_pattern = r'([A-Z0-9<]{9})[0-9]{1}([A-Z]{3})[0-9]{7}[A-Z]{1}[0-9]{7}[A-Z0-9<]{14}[0-9]{1}[0-9]{1}'
        mrz_match = re.search(mrz_pattern, full_text.replace(" ", ""))
        if mrz_match:
            print("MRZ Found! Using high-reliability data.")
            data["doc_number"] = mrz_match.group(1).replace("<", "")
            
            # Estrazione nazionalità da MRZ (es. ITA, FRA, DEU)
            nat_code = mrz_match.group(2)
            nat_map = {"ITA": "ITALIANA", "FRA": "FRANCESE", "DEU": "TEDESCA", "ESP": "SPAGNOLA"}
            data["nationality"] = nat_map.get(nat_code, nat_code)

        for doc_type, pattern in patterns.items():
            match = re.search(pattern, full_text)
            if match:
                data["doc_number"] = match.group(1)
                data["doc_type"] = doc_type
                break

        # Ricerca Cognome e Nome tramite parole chiave
        lines = [res[1].upper() for res in ocr_results]
        for i, line in enumerate(lines):
            # Cerca COGNOME / SURNAME
            if any(key in line for key in ["COGNOME", "SURNAME", "NAME", "NOM"]):
                # Prova a prendere la riga successiva o il testo dopo i due punti
                clean_line = re.sub(r'(COGNOME|SURNAME|NOME|NAME|NOM|[:])', '', line).strip()
                if not clean_line and i + 1 < len(lines):
                    clean_line = lines[i+1].strip()
                
                if "COGNOME" in line or "SURNAME" in line:
                    data["surname"] = clean_line
                elif "NOME" in line or "NAME" in line or "NOM" in line:
                    data["name"] = clean_line

        return data

    def parse_security_table(self, image_path):
        """
        Parsa la tabella delle chiavi (matrice di numeri).
        Restituisce un dizionario {sezione: {posizione: valore}}.
        """
        results = self.reader.readtext(image_path)
        # Ordiniamo per posizione Y (righe) e poi X (colonne)
        sorted_results = sorted(results, key=lambda x: (x[0][0][1], x[0][0][0]))
        
        table_data = {}
        # Logica di estrazione basata sulla struttura della tabella Alloggiati Web
        # Solitamente sono 10 sezioni con 5 numeri ciascuna
        current_section = 1
        current_pos = 1
        
        for res in sorted_results:
            text = res[1].strip()
            if text.isdigit() and len(text) <= 3: # I numeri sono solitamente di 2 o 3 cifre
                if str(current_section) not in table_data:
                    table_data[str(current_section)] = {}
                
                table_data[str(current_section)][str(current_pos)] = text
                
                current_pos += 1
                if current_pos > 5: # Salta alla sezione successiva dopo 5 numeri
                    current_pos = 1
                    current_section += 1
        
        return table_data
    # Test stub
    # engine = OCREngine()
    # print(engine.parse_guest_data(engine.extract_text("path/to/test.jpg")))
    pass
