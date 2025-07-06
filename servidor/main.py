from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests, base64

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # ponla en Railway → Settings → Variables

app = Flask(__name__)
CORS(app)

# ---------- ENDPOINT BÁSICO ----------
@app.route("/")
def inicio():
    return "Servidor Mi Alexa – OK"

# ---------- SPEECH → TEXT ----------
@app.route("/stt", methods=["POST"])
def stt():
    audio = request.data
    if not audio:
        return jsonify({"error": "No se envió audio"}), 400

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
    r = requests.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers=headers,
        files=files,
        data=data,
        timeout=60
    )
    if r.status_code == 200:
        return r.json()["text"]
    return jsonify(r.json()), r.status_code

# ---------- CHAT ----------
@app.route("/chat", methods=["POST"])
def chat():
    body = request.get_json(silent=True) or {}
    mensaje = body.get("mensaje", "")
    if not mensaje:
        return jsonify({"error": "mensaje vacío"}), 400

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    json = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": mensaje}
        ]
    }
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=json,
        timeout=30
    )
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"].strip()
    return jsonify(r.json()), r.status_code

# ---------- TEXT → SPEECH ----------
@app.route("/tts", methods=["POST"])
def tts():
    body = request.get_json(silent=True) or {}
    texto = body.get("texto", "")
    if not texto:
        return jsonify({"error": "texto vacío"}), 400

    # Ejemplo rápido con VoiceRSS (≤350 caracteres); usa tu key propia
    key = os.getenv("VOICERSS_KEY", "YOUR_VOICERSS_KEY")
    url = (
        f"https://api.voicerss.org/?key={key}"
        f"&hl=es-mx&c=MP3&src={requests.utils.quote(texto)}"
    )
    return jsonify(url)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

