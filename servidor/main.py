from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import os
from pydub import AudioSegment
import tempfile

app = Flask(__name__)
CORS(app)

# Cargar modelo Whisper solo una vez
modelo = None

@app.route("/")
def inicio():
    return "Servidor de Mi Alexa funcionando 🚀"

@app.route("/stt", methods=["POST"])
def stt():
    audio_data = request.data
    if not audio_data:
        return jsonify({"error": "No se envió audio"}), 400

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            f.flush()
            f.close()

            audio = whisper.load_audio(f.name)
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(modelo.device)
            options = whisper.DecodingOptions(language="es")
            result = whisper.decode(modelo, mel, options)

            os.remove(f.name)
            return result.text
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mensaje = data.get("mensaje", "")
    if not mensaje:
        return jsonify({"error": "Mensaje vacío"}), 400
    respuesta = f"Recibí tu mensaje: '{mensaje}'"
    return jsonify(respuesta)

@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    texto = data.get("texto", "")
    if not texto:
        return jsonify({"error": "Texto vacío"}), 400
    url = f"https://api.voicerss.org/?key=YOUR_API_KEY&hl=es-mx&src={texto}"
    return jsonify(url)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

