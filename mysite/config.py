import requests

TOKEN = "7548080659:AAEWmjL4sEYKZ5wVvgeA2JVM9c_H6aUbB7Q"
CHAT_IDS = ["2132792365", "75355402"]  # список получателей

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        payload = {"chat_id": chat_id, "text": text}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Ошибка отправки в Telegram {chat_id}: {e}")