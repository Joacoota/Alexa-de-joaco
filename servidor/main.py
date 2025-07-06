from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import tempfile
import os
import whisper

# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Tu clave de OpenAI (se recomienda usar variable de entorno)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cargar modelo Whisper (usa "base" para menos uso de RAM en Railway)
whisper_model = whisper.load_model("base")

@app.route("/")
def inicio():
    return "Servidor de Mi Alexa - funcionando 🚀"

@app.route("/stt", methods=["POST"])
def stt():
    if request.data:
        try:
            # Guardar archivo temporalmente
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(request.data)
                f.flush()
                audio_path = f.name

            # Transcribir con Whisper
            result = whisper_model.transcribe(audio_path)
            texto = result["text"]
            os.remove(audio_path)  # limpiar

            return jsonify({"texto": texto})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "No se recibió audio"}), 400

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mensaje = data.get("mensaje", "")
    if not mensaje:
        return jsonify({"error": "Falta el mensaje"}), 400

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": mensaje}]
        )
        texto = respuesta.choices[0].message.content.strip()
        return jsonify(texto)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    texto = data.get("texto", "")
    if not texto:
        return jsonify({"error": "Falta el texto"}), 400

    # VoiceRSS API
    key = os.getenv("VOICERSS_KEY")
    if not key:
        return jsonify({"error": "Falta la clave de VoiceRSS"}), 500

    import requests
    try:
        params = {
            "key": key,
            "hl": "es-mx",
            "src": texto,
            "c": "MP3",
            "f": "44khz_16bit_stereo"
        }
        response = requests.get("https://api.voicerss.org/", params=params)
        if response.status_code == 200:
            # Guardar en archivo temporal y devolver URL
            filename = "respuesta.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            return jsonify(f"http://{request.host}/{filename}")
        else:
            return jsonify({"error": "Error en VoiceRSS"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
