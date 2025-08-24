import sqlite3
from flask import Flask, render_template, url_for, redirect, request, jsonify

app = Flask(__name__)

DB = "beauty.db"

# ---------------------- Работа с БД ----------------------
def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------- Маршруты ----------------------

# Главная страница
@app.route('/home')
def home():
    return render_template('index.html')


# Страница после обработки (пример)
@app.route('/success', methods=["GET", 'POST'])
def success():
    return render_template('booking.html')

@app.route("/admin")
def admin():
    return render_template("admin_panel.html")


# О нас
@app.route("/about", methods=["POST"])
def about():
    return render_template("sidebar_1_about_us.html")

# Услуги
@app.route("/services", methods=["POST"])
def services():
    return render_template("sidebar_2_services.html")

# Примеры работ
@app.route("/examples", methods=["POST"])
def examples():
    return render_template("sidebar_3_examples_of_work.html")

# Контакты
@app.route("/contacts", methods=["POST"])
def contacts():
    return render_template("sidebar_4_contacts.html")

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

    return redirect(url_for("success"))

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