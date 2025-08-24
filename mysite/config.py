import requests

TOKEN = "7548080659:AAEWmjL4sEYKZ5wVvgeA2JVM9c_H6aUbB7Q"
CHAT_ID = "2132792365"  # сюда будут приходить уведомления

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
