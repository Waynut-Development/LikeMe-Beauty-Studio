import telebot
from config import TELEGRAM_BOT_TOKEN
from scheduler_ import get_schedule_for_day, get_schedule_for_week, get_schedule_for_month

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['day'])
def send_today_schedule(message):
    schedule = get_schedule_for_day()
    bot.send_message(message.chat.id, schedule)

@bot.message_handler(commands=['week'])
def send_week_schedule(message):
    schedule = get_schedule_for_week()
    bot.send_message(message.chat.id, schedule)

@bot.message_handler(commands=['month'])
def send_month_schedule(message):
    schedule = get_schedule_for_month()
    bot.send_message(message.chat.id, schedule)

@bot.message_handler(commands=['export'])
def send_export(message):
    with open("schedule_export.xlsx", "rb") as f:
        bot.send_document(message.chat.id, f)

if __name__ == '__main__':
    bot.polling()
