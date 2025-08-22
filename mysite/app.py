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
@app.route('/')
def home():
    return render_template('index.html')


# Обработчик кнопки (пример теста)
@app.route('/testper', methods=['POST'])
def testper():
    return redirect(url_for('success'))


# Страница после обработки (пример)
@app.route('/success')
def success():
    return render_template('booking.html')

# О нас
@app.route("/about", methods=["POST"])
def about():
    return redirect(url_for("about_page"))

@app.route("/about_page")
def about_page():
    return render_template("sidebar_1_about_us.html")


# Услуги
@app.route("/services", methods=["POST"])
def services():
    return redirect(url_for("services_page"))

@app.route("/services_page")
def services_page():
    return render_template("sidebar_2_services.html")


# Примеры работ
@app.route("/examples", methods=["POST"])
def examples():
    return redirect(url_for("examples_page"))

@app.route("/examples_page")
def examples_page():
    return render_template("sidebar_3_examples_of_work.html")


# Контакты
@app.route("/contacts", methods=["POST"])
def contacts():
    return redirect(url_for("contacts_page"))

@app.route("/contacts_page")
def contacts_page():
    return render_template("sidebar_4_contacts.html")




# ---------------------- Запись клиента ----------------------
@app.route("/book", methods=["POST"])
def book():
    name = request.form.get("name")
    phone = request.form.get("phone")
    service = request.form.get("service")
    date = request.form.get("date")
    time = request.form.get("time")

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO appointments (name, phone, service, date, time) VALUES (?, ?, ?, ?, ?)",
        (name, phone, service, date, time),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("success"))


# ---------------------- Админ-панель расписания ----------------------
# Получить расписание
@app.route("/schedule", methods=["GET"])
def get_schedule():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM schedule").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

# Сохранить расписание
@app.route("/schedule", methods=["POST"])
def save_schedule():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Нет данных"}), 400

    conn = get_db_connection()
    for cell in data:  # [{date, time, status}, ...]
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