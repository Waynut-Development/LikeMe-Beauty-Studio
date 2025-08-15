# from apscheduler.schedulers.background import BackgroundScheduler
# #from models import db, Appointment, User
# from sms_utils import send_sms_code
# from telegram_utils_ import send_telegram_message
# import datetime

# def notify_clients():
#     tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
#     date_str = tomorrow.strftime('%Y-%m-%d')
#     appointments = Appointment.query.filter(Appointment.datetime.contains(date_str)).all()
#     for app in appointments:
#         user = User.query.get(app.user_id)
#         if user:
#             send_sms_code(user.phone)  # Здесь можно заменить на полноценное SMS-напоминание
#             send_telegram_message(f"Напоминание отправлено клиенту: {user.phone}")

# scheduler = BackgroundScheduler()
# scheduler.add_job(notify_clients, 'interval', hours=24)
# scheduler.start()
