import sqlite3
from flask import Flask, render_template, url_for, redirect, request, jsonify
from config import send_telegram_message

app = Flask(__name__)

DB = "beauty.db"

# ---------------------- Работа с БД ----------------------
def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------- Маршруты ----------------------

# Главная страница
@app.route('/')
def home():
    return render_template('index.html')


# Страница после обработки (пример)
@app.route('/success', methods=["GET", 'POST'])
def success():
    return render_template('booking.html')

@app.route("/admin")
def admin():
    return render_template("admin_panel.html")


# # О нас
# @app.route("/about", methods=["POST"])
# def about():
#     return render_template("sidebar_1_about_us.html")

# # Услуги
# @app.route("/services", methods=["POST"])
# def services():
#     return render_template("sidebar_2_services.html")

# # Примеры работ
# @app.route("/examples", methods=["POST"])
# def examples():
#     return render_template("sidebar_3_examples_of_work.html")

# # Контакты
# @app.route("/contacts", methods=["POST"])
# def contacts():
#     return render_template("sidebar_4_contacts.html")

# отмена или перенос
@app.route("/canceling_rescheduling", methods=["POST"])
def canceling_rescheduling():
    return render_template("canceling or rescheduling.html")

# отмена записи
@app.route("/canceling", methods=["POST"])
def canceling():
    return render_template("canceling.html")

# перенос записи
@app.route("/rescheduling", methods=["POST"])
def rescheduling():
    return render_template("rescheduling.html")



# ---------- Получить свободные слоты ----------
@app.route("/free_slots/<date>")
def free_slots(date):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT time FROM schedule WHERE date=? AND status='free' ORDER BY time",
        (date,)
    ).fetchall()
    conn.close()
    return jsonify([row["time"] for row in rows])

# ---------- Запись клиента ----------
@app.route("/book", methods=["GET", "POST"])
def book():
    name = request.form.get("name")
    phone = request.form.get("phone")
    service = request.form.get("service")
    date = request.form.get("date")
    time = request.form.get("time")

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO appointments (name, phone, service, date, time) VALUES (?, ?, ?, ?, ?)",
        (name, phone, service, date, time)
    )
    conn.execute(
        "UPDATE schedule SET status='busy' WHERE date=? AND time=?",
        (date, time)
    )
    conn.commit()
    conn.close()

    # 🚀 Отправляем уведомление в Telegram
    message = (
        f"📅 Новая запись!\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Услуга: {service}\n"
        f"Дата: {date}\n"
        f"Время: {time}"
    )
    send_telegram_message(message)

    return redirect(url_for("success"))

# ---------- Отмена записи ----------
@app.route("/cancel", methods=["POST"])
def cancel():
    name = request.form.get("name")
    phone = request.form.get("phone")
    service = request.form.get("service")
    date = request.form.get("date")

    conn = get_db_connection()

    # ищем запись
    appointment = conn.execute(
        "SELECT * FROM appointments WHERE name=? AND phone=? AND service=? AND date=?",
        (name, phone, service, date)
    ).fetchone()

    if not appointment:
        conn.close()
        return jsonify({"error": "Запись не найдена"}), 404

    # освобождаем слот
    conn.execute(
        "UPDATE schedule SET status='free' WHERE date=? AND time=?",
        (appointment["date"], appointment["time"])
    )

    # удаляем запись
    conn.execute("DELETE FROM appointments WHERE id=?", (appointment["id"],))
    conn.commit()
    conn.close()

    # уведомление в Telegram
    message = (
        f"❌ Отмена записи\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Услуга: {service}\n"
        f"Дата: {date}"
    )
    send_telegram_message(message)

    return render_template("canceling.html", success=True)


# ---------- Перенос записи ----------
@app.route("/reschedule", methods=["POST"])
def reschedule():
    name = request.form.get("name")
    phone = request.form.get("phone")
    service = request.form.get("service")
    old_date = request.form.get("old_date")
    old_time = request.form.get("old_time")
    new_date = request.form.get("date")
    new_time = request.form.get("time")

    conn = get_db_connection()

    # ищем старую запись
    appointment = conn.execute(
        "SELECT * FROM appointments WHERE name=? AND phone=? AND service=? AND date=? AND time=?",
        (name, phone, service, old_date, old_time)
    ).fetchone()

    if not appointment:
        conn.close()
        return jsonify({"error": "Запись не найдена"}), 404

    # освободить старый слот
    conn.execute(
        "UPDATE schedule SET status='free' WHERE date=? AND time=?",
        (old_date, old_time)
    )

    # занять новый слот
    conn.execute(
        "UPDATE schedule SET status='busy' WHERE date=? AND time=?",
        (new_date, new_time)
    )

    # обновить запись
    conn.execute(
        "UPDATE appointments SET date=?, time=? WHERE id=?",
        (new_date, new_time, appointment["id"])
    )

    conn.commit()
    conn.close()

    # уведомление в Telegram
    message = (
        f"🔄 Перенос записи\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Услуга: {service}\n"
        f"С {old_date} {old_time}\n"
        f"На {new_date} {new_time}"
    )
    send_telegram_message(message)

    return render_template("rescheduling.html", success=True)


# ---------- Расписание (API для админки) ----------
@app.route("/schedule", methods=["GET"])
def get_schedule():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM schedule").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/schedule", methods=["POST"])
def save_schedule():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Нет данных"}), 400

    conn = get_db_connection()
    for cell in data:
        conn.execute(
            """
            INSERT INTO schedule (date, time, status)
            VALUES (?, ?, ?)
            ON CONFLICT(date, time) DO UPDATE SET status=excluded.status
            """,
            (cell["date"], cell["time"], cell["status"])
        )
    conn.commit()
    conn.close()
    return jsonify({"message": "Расписание сохранено!"})


# ---------------------- Запуск ----------------------
if __name__ == '__main__':
    app.run(debug=True)