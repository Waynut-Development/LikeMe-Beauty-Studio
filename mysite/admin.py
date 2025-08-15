from flask import Blueprint, request, render_template
#from models import Appointment, db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    return 'Админка — сюда можно вставить HTML шаблон'

# @admin_bp.route('/block-time', methods=['POST'])
# def block_time():
#     time_slot = request.form['time']
#     a = Appointment(datetime=time_slot, service="Blocked", status="unavailable")
#     db.session.add(a)
#     db.session.commit()
#     return 'Заблокировано'
