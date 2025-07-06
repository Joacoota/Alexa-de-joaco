
import os
import wave
import openai
import requests
from flask import Flask, request, jsonify
from pydub import AudioSegment

# --- Configuración de OpenAI ---
openai.api_key = "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"  # Coloca tu clave aquí

# --- Flask Setup ---
app = Flask(__name__)

# Ruta para recibir el audio WAV y convertirlo a texto (STT)
@app.route("/stt", methods=["POST"])
def stt():
    try:
        # Recibir el archivo de audio
        audio_file = request.data
        with open("audio.wav", "wb") as f:
            f.write(audio_file)

        # Usar la API de Whisper para convertir a texto
        audio = open("audio.wav", "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio)
        text = transcript['text']

        return jsonify(text=text)
    except Exception as e:
        print(f"Error en STT: {e}")
        return jsonify(error="Error procesando el audio"), 500

# Ruta para recibir el mensaje de texto, obtener la respuesta IA y convertirla a audio
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data['mensaje']

        # Consulta a OpenAI para obtener una respuesta
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=user_message,
            max_tokens=150
        )
        answer = response.choices[0].text.strip()

        return jsonify(text=answer)
    except Exception as e:
        print(f"Error en Chat: {e}")
        return jsonify(error="Error procesando la respuesta"), 500

# Ruta para convertir texto en voz (TTS) y devolver la URL del archivo MP3
@app.route("/tts", methods=["POST"])
def tts():
    try:
        data = request.get_json()
        text = data["texto"]

        # Usar un servicio TTS como VoiceRSS para convertir el texto en MP3
        tts_url = f"http://api.voicerss.org/?key=tu_clave_api_voicerss&hl=es-es&src={text}"
        response = requests.get(tts_url)

        if response.status_code == 200:
            with open("response.mp3", "wb") as f:
                f.write(response.content)

            # Devolver la URL del archivo MP3 generado
            return jsonify(url="https://<tu-url-publica>.railway.app/response.mp3")

        return jsonify(error="Error generando el TTS"), 500
    except Exception as e:
        print(f"Error en TTS: {e}")
        return jsonify(error="Error procesando el texto"), 500

# Ruta para servir el archivo MP3 generado
@app.route("/response.mp3")
def serve_mp3():
    return send_file("response.mp3", mimetype="audio/mp3")

# Iniciar el servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
