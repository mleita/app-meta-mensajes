from flask import Flask, request
import os
import requests
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")   # LTAT guardado en .env
PIXEL_ID = os.getenv("PIXEL_ID")           # ID de tu Pixel
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")   # Token de verificación para Meta

app = Flask(__name__)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verificación inicial con Meta
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Error de verificación", 403

    elif request.method == "POST":
        data = request.json
        print("Mensaje recibido:", data)

        # Extraer teléfono y mensaje
        try:
            telefono = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
            mensaje = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
            enviar_evento(mensaje, telefono)
        except Exception as e:
            print("Error procesando mensaje:", e)

        return "EVENT_RECEIVED", 200

def enviar_evento(mensaje, telefono):
    url = f"https://graph.facebook.com/v19.0/{PIXEL_ID}/events"
    payload = {
        "data": [{
            "event_name": "MensajeEnviado",
            "event_time": int(time.time()),
            "user_data": {
                "ph": telefono
            },
            "custom_data": {
                "mensaje": mensaje
            }
        }],
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, json=payload)
    print("Evento enviado:", r.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
