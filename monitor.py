import google.generativeai as genai
import datetime
import requests
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi API Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

def get_ssh_attempts():
    result = subprocess.check_output(
        "grep 'Failed password' /var/log/auth.log | tail -n 10",
        shell=True
    )
    return result.decode()

def get_gemini_analysis(log_text):
    try:
        response = model.generate_content(
            f"""Kamu adalah analis keamanan server Linux.
Analisis log SSH attack berikut dan balas dalam Bahasa Indonesia.

LOG:
{log_text}

Balas HANYA dengan format ini (singkat & padat):
LEVEL ANCAMAN: [RENDAH/SEDANG/TINGGI/KRITIS]
ANALISIS: [1-2 kalimat penjelasan]
TINDAKAN SEGERA:
1. [tindakan spesifik]
2. [tindakan spesifik]"""
        )
        return response.text
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