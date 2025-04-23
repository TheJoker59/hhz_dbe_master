import gradio as gr
import os
from azure_chat import chat_with_azure
from file_handler import handle_file

# Port konfigurieren
port = int(os.environ.get("WEBSITE_PORT", 7860))

# Logo URL
logo_path = "https://kipu-quantum.com/basisTheme/common/logo.png"

# Einfaches CSS für das Logo
custom_css = """
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
}

.title {
    margin-left: 10px;
    flex-grow: 1;
}
"""

# GUI aufbauen
with gr.Blocks(css=custom_css) as demo:
    # Logo als HTML-Element einfügen
    with gr.Row(elem_classes="logo-container"):
        gr.HTML(f'<img src="{logo_path}" class="logo-image" alt="Logo" />')
        gr.Markdown("## 💬 Chat mit Azure + Datei-Upload", elem_classes="title")

    # Zustands-Objekt für Datei
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
    
    # Starte den Server
    demo.launch(server_name="0.0.0.0", server_port=port)