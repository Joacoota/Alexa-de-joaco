from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
import io
import wave

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Tu clave API de OpenAI (la que proporcionaste)
openai.api_key = "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"

# Configuración del servidor de TTS (VoiceRSS)
TTS_API_KEY = '45f4a3eee38f402eae96e53f8a3777d5'

@app.route('/')
def hello_world():
    return "Servidor de Mi Alexa - funcionando 🚀"

@app.route('/stt', methods=['POST'])
def stt():
    audio_file = request.data  # El archivo de audio viene directamente en el cuerpo de la solicitud

    # Convierte los datos binarios a un formato adecuado para enviar a OpenAI Whisper
    audio = io.BytesIO(audio_file)
    
    # Llamada a la API de OpenAI Whisper para transcripción de voz a texto
    try:
        transcript = openai.Audio.transcribe("whisper-1", audio)
        return jsonify({"transcription": transcript['text']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('mensaje')

    if not user_message:
        return jsonify({"error": "No message received"}), 400

    # Llamada a la API de OpenAI GPT-3.5 para generar la respuesta
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo", 
            prompt=user_message,
            max_tokens=150
        )
        return jsonify({"respuesta": response.choices[0].text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('texto')

    if not text:
        return jsonify({"error": "No text received"}), 400

    # Solicitar al servicio TTS (VoiceRSS) la conversión de texto a audio
    try:
        url = f"http://api.voicerss.org/?key={TTS_API_KEY}&hl=en-us&src={text}&c=MP3"
        audio_data = requests.get(url).content

        # Guarda el audio en memoria
        audio = io.BytesIO(audio_data)
        return audio.getvalue()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
