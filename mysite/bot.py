import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="bot.log",
)
logger = logging.getLogger(__name__)

def get_data(period: str):
    try:
        conn = sqlite3.connect("beauty.db")
        cursor = conn.cursor()

        now = datetime.now()
        if period == "day":
            start_date, end_date = now.date(), now.date()
        elif period == "week":
            start_date, end_date = now.date(), now.date() + timedelta(days=7)
        elif period == "month":
            start_date, end_date = now.date(), now.date() + timedelta(days=30)
        else:
            return ["Некорректный период."]

        cursor.execute(
            "SELECT service, date, time, phone FROM appointments WHERE date BETWEEN ? AND ? ORDER BY date, time",
            (str(start_date), str(end_date)),
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return ["Нет записей на выбранный период."]

        return [f"Услуга: {s}\nДата: {d}\nВремя: {t}\nТелефон: {p}" for s, d, t, p in rows]
    except Exception as e:
        logger.error(f"Ошибка БД: {e}")
        return ["Ошибка при получении данных."]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [[KeyboardButton("/day"), KeyboardButton("/week"), KeyboardButton("/month")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Привет, {user.first_name}! Выбери период:",
        reply_markup=reply_markup,
    )

async def day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\n\n".join(get_data("day")))

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\n\n".join(get_data("week")))

async def month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\n\n".join(get_data("month")))

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Неизвестная команда.")

def main():
    TOKEN = "7548080659:AAEWmjL4sEYKZ5wVvgeA2JVM9c_H6aUbB7Q"
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("day", day))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("month", month))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    app.run_polling()

if __name__ == "__main__":
    main()
