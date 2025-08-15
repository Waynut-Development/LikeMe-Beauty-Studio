import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


TELEGRAM_BOT_TOKEN = '7548080659:AAEWmjL4sEYKZ5wVvgeA2JVM9c_H6aUbB7Q'
TELEGRAM_CHAT_ID = '2132792365'

SMS_API_KEY = 'E76828B7-D8EC-6324-1BA0-2534C70FA867'

# Flask Secret Key
SECRET_KEY = 'ваш_секретный_ключ'  # Сгенерируйте случайный ключ

# Другие настройки
DEBUG = False