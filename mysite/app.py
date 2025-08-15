import os
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

from werkzeug.security import generate_password_hash, check_password_hash
import requests
#from models import User, Appointment, Service
from sms_utils import send_sms_code, verify_sms_code
from telegram_utils_ import send_telegram_message
from admin import admin_bp
from config import Config
#from extensions import db


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()



app.secret_key = os.urandom(24)

# Конфигурация базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'database.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)


app.secret_key = 'your_secret_key'
app.config.from_object('config')

app.register_blueprint(admin_bp)



app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TELEGRAM_BOT_TOKEN'] = '7548080659:AAEWmjL4sEYKZ5wVvgeA2JVM9c_H6aUbB7Q'
app.config['TELEGRAM_CHAT_ID'] = '2132792365'
app.config['WORKING_HOURS'] = {'start': 9, 'end': 20}
app.config['TIME_SLOT_MINUTES'] = 30

#db = SQLAlchemy(app)

# # Модели данных
# class Service(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     price = db.Column(db.Integer, nullable=False)
#     duration = db.Column(db.Integer, nullable=False)
#     category = db.Column(db.String(50))

# class Appointment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     phone = db.Column(db.String(20), nullable=False)
#     service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
#     date = db.Column(db.String(10), nullable=False)
#     time = db.Column(db.String(5), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)

#     service = db.relationship('Service', backref='appointments')

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)

# Инициализация базы данных
def init_db():
    with app.app_context():
        db.create_all()

        if not Service.query.first():
            services = [
                Service(name="Мужская стрижка", price=1000, duration=30),
                Service(name="Женская стрижка (короткие)", price=1500, duration=60),
                Service(name="Женская стрижка (средние)", price=2000, duration=60),
                Service(name="Женская стрижка (длинные)", price=2500, duration=90),
                Service(name="Детская стрижка", price=800, duration=30),
                Service(name="Стрижка бороды и усов", price=500, duration=30),
                Service(name="Комуфлирование волос", price=1000, duration=60),
                Service(name="Комуфлирование бороды", price=500, duration=30),
                Service(name="Сложное окрашивание", price=7000, duration=180),
                Service(name="Кератин/ботокс волос", price=4000, duration=120),
                Service(name="Холодное восстановление волос", price=2500, duration=90),
                Service(name="Окрашивание волос", price=2500, duration=120),
                Service(name="Заблокировано", price=0, duration=30)
            ]
            db.session.add_all(services)

            if not User.query.first():
                admin = User(
                    username="admin",
                    password=generate_password_hash("admin123")
                )
                db.session.add(admin)

            db.session.commit()

init_db()

# Telegram уведомления
def send_telegram_notification(message):
    try:
        url = f"https://api.telegram.org/bot{app.config['TELEGRAM_BOT_TOKEN']}/sendMessage"
        response = requests.post(url, json={
            'chat_id': app.config['TELEGRAM_CHAT_ID'],
            'text': message,
            'parse_mode': 'HTML'
        })
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return False
# Главные маршруты
@app.route('/')
def home():
    services = Service.query.filter(Service.name != "Заблокировано").all()
    min_date = datetime.now().strftime('%Y-%m-%d')
    max_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
    return render_template('index.html')



@app.route('/book', methods=['POST'])
def book():
    if request.method == 'POST':
        try:
            service = Service.query.get(request.form['service'])
            if not service:
                flash('Услуга не найдена', 'error')
                return redirect(url_for('home'))

            appointment = Appointment(
                name=request.form['name'],
                date=request.form['date'],
                time=request.form['time'],
                phone=request.form['phone'],
                service_id=service.id
            )

            # Проверка формата времени
            try:
                datetime.strptime(appointment.time, '%H:%M')
            except ValueError:
                flash('Неверный формат времени', 'error')
                return redirect(url_for('home'))

            # Проверка занятости времени
            if Appointment.query.filter_by(date=appointment.date, time=appointment.time).first():
                flash('Это время уже занято', 'error')
                return redirect(url_for('home'))

            db.session.add(appointment)
            db.session.commit()

            # Отправка в Telegram
            message = f"""
            ✨ <b>Новая запись!</b>
            ├ <b>Имя:</b> {appointment.name}
            ├ <b>Телефон:</b> {appointment.phone}
            ├ <b>Услуга:</b> {service.name}
            ├ <b>Дата:</b> {appointment.date}
            └ <b>Время:</b> {appointment.time}
            """
            if not send_telegram_notification(message):
                print("Не удалось отправить уведомление в Telegram")

            flash('Вы успешно записаны! Мы скоро свяжемся с вами.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при записи. Пожалуйста, попробуйте позже.', 'error')
            print(f"Ошибка записи: {e}")

        return redirect(url_for('book'))

# Админ-панель
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Заполните все поля', 'error')
            return render_template('admin/login.html')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))

        flash('Неверные данные для входа', 'error')

    return render_template('admin/login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        session['phone'] = phone
        code = send_sms_code(phone)
        return render_template('verify.html', phone=phone)
    return render_template('login.html')

@app.route('/verify', methods=['POST'])
def verify():
    code = request.form['code']
    phone = session.get('phone')
    if verify_sms_code(phone, code):
        session['authenticated'] = True
        return redirect(url_for('index'))
    return render_template('verify.html', error="Неверный код", phone=phone)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/cancel/<int:appointment_id>', methods=['POST'])
def cancel(appointment_id):
    if 'authenticated' in session:
        appt = Appointment.query.get(appointment_id)
        if appt and appt.client_phone == session['phone']:
            db.session.delete(appt)
            db.session.commit()
            return redirect(url_for('index'))
    return "Неавторизованный доступ", 403


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    try:
        current_date = date.today()
        week_days = []

        for day_offset in range(7):
            day_date = current_date + timedelta(days=day_offset)
            time_slots = []

            for hour in range(app.config['WORKING_HOURS']['start'], app.config['WORKING_HOURS']['end']):
                for minute in [0, 30]:
                    time_str = f"{hour:02d}:{minute:02d}"

                    # Ищем запись на это время
                    appointment = db.session.query(Appointment).filter_by(
                        date=day_date.strftime('%Y-%m-%d'),
                        time=time_str
                    ).first()

                    # Формируем информацию о слоте
                    slot_info = {
                        'time': time_str,
                        'is_booked': appointment is not None,
                        'client_name': '',
                        'appointment_id': None,
                        'service_name': ''
                    }

                    if appointment:
                        slot_info['client_name'] = appointment.name if appointment.name else ''
                        slot_info['appointment_id'] = appointment.id if appointment.id else None
                        if appointment.service:
                            slot_info['service_name'] = appointment.service.name if appointment.service.name else ''

                    time_slots.append(slot_info)

            week_days.append({
                'date': day_date,
                'date_str': day_date.strftime('%Y-%m-%d'),
                'time_slots': time_slots
            })

        return render_template('admin/dashboard.html',
                            week_days=week_days,
                            current_date=current_date)

    except Exception as e:
        print(f"Ошибка в админ-панели: {str(e)}")
        flash('Ошибка загрузки расписания', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/api/free-slot', methods=['POST'])
def admin_api_free_slot():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({'success': False, 'error': 'Invalid data'}), 400

        appointment = Appointment.query.get(data['id'])
        if appointment:
            db.session.delete(appointment)
            db.session.commit()
            return jsonify({'success': True})

        return jsonify({'success': False, 'error': 'Appointment not found'}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/api/block-slot', methods=['POST'])
def admin_api_block_slot():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        if not data or 'date' not in data or 'time' not in data:
            return jsonify({'success': False, 'error': 'Invalid data'}), 400

        # Проверяем, не занято ли уже время
        existing = Appointment.query.filter_by(
            date=data['date'],
            time=data['time']
        ).first()

        if existing:
            return jsonify({'success': False, 'error': 'Slot already booked'}), 400

        blocked_service = Service.query.filter_by(name="Заблокировано").first()
        if not blocked_service:
            return jsonify({'success': False, 'error': 'Blocked service not found'}), 500

        blocked_appointment = Appointment(
            name="Заблокировано",
            phone="0000000000",
            service_id=blocked_service.id,
            date=data['date'],
            time=data['time']
        )

        db.session.add(blocked_appointment)
        db.session.commit()

        return jsonify({
            'success': True,
            'appointment_id': blocked_appointment.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)