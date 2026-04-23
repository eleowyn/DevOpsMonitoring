import datetime
import requests
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi Vertex AI REST API
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.0-flash"
VERTEX_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def get_ssh_attempts():
    result = subprocess.check_output(
        "grep 'Failed password' /var/log/auth.log | tail -n 10",
        shell=True
    )
    return result.decode()

def get_gemini_analysis(log_text):
    try:
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"Ada percobaan login brute force:\n{log_text}\n"
                                f"Apa yang sebaiknya saya lakukan? responnya jangan terlalu panjang"
                            )
                        }
                    ]
                }
            ]
        }
        response = requests.post(
            VERTEX_URL,
            headers={"Content-Type": "application/json"},
            json=payload
        )
        result = response.json()
        
        # Cek jika response tidak mengandung candidates
        if "candidates" not in result:
            error_msg = result.get("error", {}).get("message", str(result))
            return f"⚠️ Gemini error: {error_msg}"
            
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"⚠️ Gagal mendapatkan analisis dari Gemini: {e}"

def send_whatsapp(message):
    token = os.getenv("FONNTE_TOKEN")
    payload = {
        "target": os.getenv("TARGET_NUMBER"),
        "message": message,
    }
    headers = {"Authorization": token}
    r = requests.post("https://api.fonnte.com/send", data=payload, headers=headers)
    return r.status_code

# Eksekusi semua
log = get_ssh_attempts()
ai_response = get_gemini_analysis(log)
full_message = (
    f"[{datetime.datetime.now()}] ⚠️ Percobaan Login Detected!\n\n"
    f"{log}\n\n"
    f"💬 Gemini says:\n{ai_response}"
)
send_whatsapp(full_message)