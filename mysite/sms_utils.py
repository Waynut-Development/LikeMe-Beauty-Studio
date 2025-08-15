import requests
import random

sms_codes = {}

def send_sms_code(phone):
    code = random.randint(1000, 9999)
    sms_codes[phone] = code
    api_id = "E76828B7-D8EC-6324-1BA0-2534C70FA867"
    url = f"https://sms.ru/sms/send?api_id={api_id}&to={phone}&msg=Код+подтверждения:+{code}&json=1"
    requests.get(url)
    return code

def verify_sms_code(phone, code):
    return sms_codes.get(phone) == int(code)
