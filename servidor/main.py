from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Claves (configurá estas en Railway como Variables de Entorno)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VOICERSS_KEY   = os.getenv("VOICERSS_KEY")

@app.route("/")
def home():
    return "Servidor de Mi Alexa 🎙️"

@app.route("/stt", methods=["POST"])
def stt():
    try:
        # Verifica si hay archivo de audio
        audio = request.get_data()
        if not audio:
            return jsonify({"error": "No audio received"}), 400

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
        }
        files = {
            "file": ("audio.wav", audio, "audio/wav"),
            "model": (None, "whisper-1")
        }
        response = requests.post("https://api.openai.com/v1/audio/transcriptions",
                                 headers=headers, files=files)
        if response.ok:
            text = response.json()["text"]
            return text
        return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("mensaje", "")
    if not prompt:
        return jsonify({"error": "Falta mensaje"}), 400

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)

    if response.ok:
        return response.json()["choices"][0]["message"]["content"]
    return jsonify({"error": response.text}), response.status_code

@app.route("/tts", methods=["POST"])
def tts():
    data = request.json
    texto = data.get("texto", "")
    if not texto:
        return jsonify({"error": "Falta texto"}), 400

    params = {
        "key": VOICERSS_KEY,
        "hl": "es-ar",
        "src": texto,
        "c": "MP3",
        "f": "44khz_16bit_stereo"
    }
    response = requests.get("https://api.voicerss.org/", params=params)
    
    if response.ok and b'Audio' not in response.content:
        # Railway requiere que sea una URL, así que podés hacer que ESP32 lea de esta misma ruta /stream.mp3
        return jsonify({"url": response.url})
    return jsonify({"error": "TTS falló"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
