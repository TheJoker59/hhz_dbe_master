import pandas as pd
import PyPDF2

# Datei-Upload verarbeiten
def handle_file(file, file_state):
    if not file:
        return "❌ Keine Datei ausgewählt.", file_state
        
    # CSV-Datei verarbeiten
    if file.name.endswith('.csv'):
        try:
            # Prüfen ob neue Datei
            if file.name != file_state["filename"]:
                df = pd.read_csv(file)
                header_info = ", ".join(df.columns)
                preview = df.to_string(index=False)
                file_state["csv_text"] = f"Spalten: {header_info}\nVorschau:\n{preview}"
                file_state["was_sent"] = False
                file_state["filename"] = file.name
                return f"✅ Neue CSV-Datei **{file.name}** erfolgreich hochgeladen.", file_state
            else:
                return f"⚠️ Datei **{file.name}** wurde bereits verwendet.", file_state
        except Exception as e:
            return f"❌ Fehler beim Lesen der CSV-Datei: {str(e)}", file_state
    
    # PDF-Datei verarbeiten
    elif file.name.endswith('.pdf'):
        try:
            # Prüfen ob neue Datei
            if file.name != file_state["filename"]:
                # PDF-Text extrahieren
                pdf_text = ""
                with open(file.name, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)
                    
                    # Extrahiere Text aus jeder Seite
                    for page_num in range(num_pages):
                        page = pdf_reader.pages[page_num]
                        pdf_text += page.extract_text() + "\n\n"
                
                # Für sehr große PDFs: Begrenze die Textmenge
                if len(pdf_text) > 10000:
                    pdf_text = pdf_text[:10000] + "...[Text gekürzt, PDF enthält weitere Inhalte]"
                
                file_state["csv_text"] = f"PDF-Inhalt ({num_pages} Seiten):\n{pdf_text}"
                file_state["was_sent"] = False
                file_state["filename"] = file.name
                return f"✅ Neue PDF-Datei **{file.name}** ({num_pages} Seiten) erfolgreich hochgeladen.", file_state
            else:
                return f"⚠️ Datei **{file.name}** wurde bereits verwendet.", file_state
        except Exception as e:
            return f"❌ Fehler beim Lesen der PDF-Datei: {str(e)}", file_state
    
    return "❌ Ungültige Datei. Nur .csv und .pdf Dateien sind erlaubt.", file_state