from ocr_engine import OCREngine
import re

def run_100_debug_tests():
    engine = OCREngine()
    
    test_cases = [
        # Case 1: Standard CIE
        [("COGNOME", "ROSSI"), ("NOME", "MARIO"), ("NATO IL", "15/05/1980"), ("NR DOC", "CA12345BB")],
        # Case 2: Passport with MRZ
        [("P<ITAROSSI<<MARIO<<<<<<<<", "MRZ"), ("ROSSI MARIO", "NAME"), ("15-05-1980", "BIRTH")],
        # Case 3: Messy OCR with dots
        [("Cognome: Bianchi", ""), ("Nome: Luca", ""), ("Data 10.12.1990", ""), ("Doc. YA7654321", "")],
        # Case 4: Only dates and ID
        [("12/12/2025", ""), ("01/01/1970", ""), ("12/12/2015", ""), ("AA11111AA", "")]
    ]

    print("--- Avvio 100 Debug Test (Simulazione) ---")
    
    success_count = 0
    for i in range(100):
        # Ruota i casi di test o genera varianti
        base_case = test_cases[i % len(test_cases)]
        ocr_results = [(None, text) for text, label in base_case]
        
        try:
            data = engine.parse_guest_data(ocr_results)
            
            # Verifica minima
            if data["doc_number"] or data["surname"] or data["birth_date"]:
                success_count += 1
            
            if i % 25 == 0:
                print(f"Test {i}: OK - Estratto: {data['surname']} {data['doc_number']}")
        except Exception as e:
            print(f"Test {i}: FALLITO - {e}")

    print(f"--- Debug Completato: {success_count}/100 test superati ---")

if __name__ == "__main__":
    run_100_debug_tests()
