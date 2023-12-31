
import pytz
from datetime import datetime, timedelta, timezone
from flask import render_template, flash, redirect, url_for, request, jsonify, session, current_app
from flask_login import current_user, login_required
from app import db
from app.models import EnglishClasses
from flask import Blueprint

booking_bp = Blueprint('booking_bp', __name__, template_folder='templates/booking') 

@booking_bp.route('/bookings')
@login_required
def bookings():
    open_in_days = current_app.config['CLASSES_OPEN_IN_DAYS']
    delta = timedelta(days=+open_in_days)
    startDate = datetime.now(pytz.timezone(current_app.config['TZ_INFO']))
    startDate = startDate.replace(hour=0, minute=0)
    endDate = startDate + delta
    classes = EnglishClasses.query.filter(EnglishClasses.start_time >= startDate).filter(EnglishClasses.end_time <= endDate).order_by(EnglishClasses.start_time.asc()).all()
    return render_template('bookings.html', title='Make a Booking', classes=classes)


@booking_bp.route('/makebooking', methods=['POST'])
@login_required
def makeBooking():
    data = request.get_json()
    classId = int(data['classId'])
    targetClass = EnglishClasses.query.get(classId)
    studentCount = targetClass.students.count()
    maxSize = int(current_app.config['MAX_CLASS_SIZE'])
    state = ''
    if studentCount >= maxSize:
        msg = 'This class is fully booked'
    elif current_user.classes.filter_by(id=classId).first():
        msg = 'Already signed up for this class'
    else:
        targetClass.students.add(current_user)
        db.session.commit()
        studentCount += 1
        state = 'ADDED'
        msg = 'You have signed up for the class'
    return jsonify(
            {
                'message': msg,
                'studentCount': studentCount,
                'state': state
            }
        )


@booking_bp.route('/cancelbooking', methods=['POST'])
@login_required
def cancelBooking():
    data = request.get_json()
    classId = int(data['classId'])
    targetClass = EnglishClasses.query.get(classId)
    state = ''
    if not current_user.classes.filter_by(id=classId).first():
        msg = 'You have not booked this class yet'
    else:
        targetClass.students.remove(current_user)
        db.session.commit()
        msg = 'Booking cancelled'
        state = 'REMOVED'
    return jsonify(
        {
            'message': msg,
            'studentCount': targetClass.students.count(),
            'state': state
        }
    )
    

@booking_bp.route('/mybookings')
@login_required
def myBookings():
    userClasses = current_user.classes.order_by(EnglishClasses.start_time.asc()).all()
    t_zone = pytz.timezone(current_app.config['TZ_INFO'])
    return render_template('mybookings.html', title='My Bookings', userClasses=userClasses, currtime = datetime.now(t_zone), t_zone=t_zone)
