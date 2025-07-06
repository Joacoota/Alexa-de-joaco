from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = os.getenv("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")  # ← Tu clave debe estar como variable de entorno

@app.route("/")
def inicio():
    return "Servidor de Mi Alexa - funcionando 🚀"

@app.route("/stt", methods=["POST"])
def transcribir_audio():
    try:
        audio = request.data
        if not audio:
            return jsonify({"error": "No se recibió audio"}), 400

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        files = {
            "file": ("audio.wav", audio, "audio/wav")
        }
        data = {
            "model": "whisper-1",
            "language": "es"
        }
        response = requests.post("https://api.openai.com/v1/audio/transcriptions",
                                 headers=headers, files=files, data=data)

        if response.status_code != 200:
            return jsonify({"error": response.text}), 400

        texto = response.json().get("text", "")
        return texto
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def responder_chat():
    data = request.json
    mensaje = data.get("mensaje", "")
    if not mensaje:
        return jsonify({"error": "Mensaje vacío"}), 400

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    json_data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": mensaje}]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions",
                             headers=headers, json=json_data)
    if response.status_code != 200:
        return jsonify({"error": response.text}), 400

    return response.json()["choices"][0]["message"]["content"]

@app.route("/tts", methods=["POST"])
def sintetizar_audio():
    from urllib.parse import quote
    data = request.json
    texto = data.get("texto", "")
    if not texto:
        return jsonify({"error": "Texto vacío"}), 400

    VOICERSS_KEY = os.getenv("VOICERSS_KEY")  # ← clave TTS
    if not VOICERSS_KEY:
        return jsonify({"error": "Falta clave de VoiceRSS"}), 500

    url = f"https://api.voicerss.org/?key={VOICERSS_KEY}&hl=es-mx&src={quote(texto)}&c=MP3&f=16khz_16bit_mono"
    return url

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
