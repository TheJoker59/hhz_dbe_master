import os
from azure_chat import chat_with_azure
from file_handler import handle_file
import gradio as gr

# Port konfigurieren
port = int(os.environ.get("WEBSITE_PORT", 7860))

# Logo URL
logo_path = "https://docs.platform.planqk.de/logo_dark.png"

# CSS für dunkles Theme mit goldenen Rändern, aber ohne Rand am geschlossenen Accordion
custom_css = """
/* KIPU Farben definieren */
:root {
    --kipu-gold: #E2AF0E;
    --kipu-dark: #121212;
    --kipu-darker: #0A0A0A;
}

/* Grundlegendes Styling */
.logo-image { 
    max-height: 40px; 
    margin: 10px; 
    display: inline-block; 
    object-fit: contain; 
}

.logo-container { 
    display: flex; 
    align-items: center; 
    margin-bottom: 10px; 
    padding-bottom: 10px;
}

.title { 
    margin-left: 10px; 
    flex-grow: 1;
    color: #F0F0F0;
}

/* Dunkles Theme */
body, .gradio-container {
    background-color: var(--kipu-dark) !important;
    color: #F0F0F0 !important;
}

/* Hauptblock-Ränder in Gold */
.gradio-app > div {
    border: 2px solid var(--kipu-gold) !important;
    border-radius: 8px !important;
    margin: 10px !important;
}

/* Chatbereich mit goldenem Rand */
.chat-container, .chatbot-container {
    border: 1px solid var(--kipu-gold) !important;
    border-radius: 8px !important;
    padding: 10px !important;
    margin-bottom: 15px !important;
}

/* Datei-Upload-Bereich komplett ohne goldenen Rand */
.accordion {
    border: none !important;
    background-color: var(--kipu-darker) !important;
}

/* Accordion auch im geöffneten Zustand ohne Rand */
.accordion[open], .accordion.open {
    border: none !important;
}

/* Button für Accordion mit Gold hervorheben, aber ohne Rand */
.accordion > summary {
    color: var(--kipu-gold) !important;
    border: none !important;
}

/* Nur die eigentliche Upload-Fläche mit goldenem Rand */
.accordion .file-container, .accordion .file-upload {
    border: 1px solid var(--kipu-gold) !important;
    border-radius: 8px !important;
    padding: 5px !important;
    margin-top: 10px !important;
}

/* Buttons anpassen (außer im Accordion) */
button:not(.accordion button), .button-primary:not(.accordion .button-primary) { 
    border: 1px solid var(--kipu-gold) !important; 
    background-color: var(--kipu-dark) !important; 
    color: var(--kipu-gold) !important; 
}

button:not(.accordion button):hover, .button-primary:not(.accordion .button-primary):hover { 
    background-color: var(--kipu-gold) !important; 
    color: var(--kipu-dark) !important; 
}

/* Accordion-Buttons ohne Hover-Effekt */
.accordion button:hover, .accordion .button-primary:hover {
    background-color: var(--kipu-dark) !important;
    color: var(--kipu-gold) !important;
}

/* Chat-Icons in Gold */
.svelte-1ed2p3z svg, .message-feedback button svg {
    color: var(--kipu-gold) !important;
    fill: var(--kipu-gold) !important;
    stroke: var(--kipu-gold) !important;
}

/* Sendebutton in Gold */
.send-btn, .submit-btn {
    color: var(--kipu-gold) !important;
    border-color: var(--kipu-gold) !important;
}

/* Eingabefeld und Chat dunkel halten */
textarea, input[type="text"] {
    background-color: var(--kipu-darker) !important;
    color: #F0F0F0 !important;
    border: 1px solid #333 !important;
}

/* Generelle Icons in KIPU Gold */
svg {
    color: var(--kipu-gold) !important;
    stroke: var(--kipu-gold) !important;
}

/* Trennlinie unter dem Header */
header, .header {
    border-bottom: 2px solid var(--kipu-gold) !important;
}

/* Gradio Footer entfernen */
footer, .footer {
    display: none !important;
}
"""

# GUI aufbauen
with gr.Blocks(css=custom_css) as demo:
    # Logo als HTML-Element einfügen
    with gr.Row(elem_classes="logo-container"):
        gr.HTML(f'<img src="{logo_path}" class="logo-image" alt="Logo" />')

    # Zustands-Objekt für Datei
    file_state = gr.State({"csv_text": None, "filename": None, "was_sent": False})

    # ChatInterface mit State
    chatbot = gr.ChatInterface(
        fn=chat_with_azure,
        chatbot=gr.Chatbot(height=300),
        textbox=gr.Textbox(placeholder="Ask me a yes or no question", container=False, scale=7),
        additional_inputs=[file_state],
        additional_outputs=[file_state],
        type="messages",
        flagging_mode="manual",
        flagging_options=["Like", "Spam", "Inappropriate", "Other"],
        theme="ocean",
        save_history=True,
    )

    with gr.Accordion("📎 Datei hochladen", open=False):
        file_upload = gr.File(label="Upload a CSV or PDF File", file_types=[".csv", ".pdf"])
        upload_status = gr.Textbox(label="Status", interactive=False)

    clear = gr.Button("❌ Alles zurücksetzen")

    # Datei hochladen
    file_upload.change(handle_file, inputs=[file_upload, file_state], outputs=[upload_status, file_state])

    # Clear Buttons
    clear.click(lambda: None, None, chatbot, queue=False)
    clear.click(lambda: "", None, upload_status, queue=False)
    clear.click(lambda: {"csv_text": None, "filename": None, "was_sent": False}, None, file_state, queue=False)

if __name__ == "__main__":
    # Für Debugging: Zeige Umgebungsvariablen
    print("Environment variables:")
    print(f"WEBSITE_PORT: {os.environ.get('WEBSITE_PORT')}")
    print(f"Port used: {port}")

    # Starte den Server mit ausgeblendetem Footer
    demo.launch(server_name="0.0.0.0", server_port=port, show_api=False)
