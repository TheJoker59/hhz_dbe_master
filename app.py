import gradio as gr
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import json

# Azure endpoint configuration
AZURE_ENDPOINT = os.environ.get("AZURE_ENDPOINT")
AZURE_API_KEY = os.environ.get("AZURE_API_KEY")

# Port konfigurieren
port = int(os.environ.get("WEBSITE_PORT", 7860))

# Chatfunktion mit CSV-Zustand
def chat_with_azure(message, history, file_state):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AZURE_API_KEY}",
        "Accept": "application/json"
    }

    # Konvertiere History
    chat_history = []
    for i in range(0, len(history), 2):
        user_msg = history[i]["content"] if history[i]["role"] == "user" else ""
        bot_msg = history[i + 1]["content"] if i + 1 < len(history) and history[i + 1]["role"] == "assistant" else ""
        if user_msg.strip() or bot_msg.strip():
            chat_history.append({
                "inputs": {"question": user_msg},
                "outputs": {"answer": bot_msg}
            })

    # Nur beim ersten Mal CSV-Inhalt anhängen
    if file_state["csv_text"] and not file_state["was_sent"]:
        message = f"{message.strip()}\n\n[CSV-Daten hochgeladen]\n{file_state['csv_text']}"
        file_state["was_sent"] = True  # Flag setzen

    # Payload aufbauen
    payload = {
        "chat_input": message,
        "chat_history": chat_history
    }

    print("📤 Gesendeter Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = requests.post(AZURE_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get("chat_output", "⚠️ Keine Antwort erhalten."), file_state
    except Exception as e:
        return f"❌ Fehler beim Aufruf des Azure-Endpoints: {str(e)}", file_state

# Datei-Upload verarbeiten
def handle_file(file, file_state):
    if file and file.name.endswith('.csv'):
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
    return "❌ Ungültige Datei. Nur .csv erlaubt.", file_state

# GUI aufbauen
with gr.Blocks() as demo:
    gr.Markdown("## 💬 Chat mit Azure + Datei-Upload")

    # Zustands-Objekt für CSV
    file_state = gr.State({"csv_text": None, "filename": None, "was_sent": False})

    # ChatInterface mit State
    chatbot = gr.ChatInterface(
        fn=chat_with_azure,
        additional_inputs=[file_state],
        additional_outputs=[file_state],
        type="messages",
        flagging_mode="manual",
        flagging_options=["Like", "Spam", "Inappropriate", "Other"],
        save_history=True,
    )

    with gr.Accordion("📎 Datei hochladen", open=False):
        file_upload = gr.File(label="Upload a CSV File", file_types=[".csv"])
        upload_status = gr.Textbox(label="Status", interactive=False)

    clear = gr.Button("❌ Alles zurücksetzen")

    # Datei hochladen
    file_upload.change(handle_file, inputs=[file_upload, file_state], outputs=[upload_status, file_state])

    # Clear Buttons
    clear.click(lambda: None, None, chatbot, queue=False)
    clear.click(lambda: "", None, upload_status, queue=False)
    clear.click(lambda: {"csv_text": None, "filename": None, "was_sent": False}, None, file_state, queue=False)

demo.launch(server_name="0.0.0.0", server_port=port)
