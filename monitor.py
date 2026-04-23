import google.generativeai as genai
import datetime
import requests
import subprocess

# Konfigurasi API Gemini
genai.configure(api_key="AIzaSyAnKFNa7AnSRXgkokMqaMV3vCnHB3KN9NQ")

model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def get_ssh_attempts():
    result = subprocess.check_output(
        "grep 'Failed password' /var/log/auth.log | tail -n 10",
        shell=True
    )
    return result.decode()

def get_gemini_analysis(log_text):
    try:
        response = model.generate_content(
            f"Ada percobaan login brute force:\n{log_text}\n"
            f"Apa yang sebaiknya saya lakukan? responnya jangan terlalu panjang"
        )
        return response.text
    except Exception as e:
        return f"⚠️ Gagal mendapatkan analisis dari Gemini: {e}"

def send_whatsapp(message):
    token = "4wjWV9yLvnyYDvMB4M3k"
    payload = {
        "target": "628975574089",  # contoh: 6281234567890
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