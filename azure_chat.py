import os
import requests
import json

# Azure endpoint configuration
AZURE_ENDPOINT = os.environ.get("AZURE_ENDPOINT")
AZURE_API_KEY = os.environ.get("AZURE_API_KEY")

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
                "inputs": {"chat_input": user_msg},
                "outputs": {"chat_output": bot_msg}
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
