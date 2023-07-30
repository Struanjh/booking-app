import pytz
from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import current_user, login_required
from app import app, db
from app.forms import UserProfileForm
from app.models import User, EnglishClasses


@app.route('/')
def home():
    return render_template('index.html', title='Home')  

@app.route('/bookings')
@login_required
def bookings():
    classes = EnglishClasses.query.all()
    return render_template('bookings.html', title='Bookings', classes=classes)

    def nextTenDates(numdays):
        dayOne = datetime.now(pytz.timezone('Asia/Seoul'))
        date_range = [dayOne - timedelta(days=x) for x in range(numdays)]
        print(dayOne, date_range)

    def getMinMaxUtc():
        pass


@app.route('/makebooking', methods=['POST'])
@login_required
def makeBooking():
    # MAX_STUDENTS = 10
    data = request.get_json()
    classId = int(data['classId'])
    targetClass = EnglishClasses.query.get(classId)
    studentCount = targetClass.students.count()
    state = ''
    if studentCount >= MAX_CLASS_SIZE:
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



@app.route('/cancelbooking', methods=['POST'])
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
    

@app.route('/mybookings')
@login_required
def myBookings():
    userClasses = current_user.classes.all()
    return render_template('mybookings.html', userClasses=userClasses, currtime = datetime.utcnow())


@app.route('/userprofile', methods=['GET', 'POST'])
@login_required
def userProfile():
    user = User.query.filter_by(id=current_user.id).first()
    form = UserProfileForm()
    if request.method == 'GET':
        form.id.data = user.id
        form.join_date.data = user.join_date
        form.last_login.data = user.last_login
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
    else:
        if form.validate_on_submit():
            form_email = form.email.data.lower()
            email_in_use = User.query.filter_by(email=form_email).first()
            print(current_user.email)
            print(form_email)
            print(email_in_use)
            if email_in_use and form_email != current_user.email:
                flash('This email is already in use. Please select a different email')
                return redirect(url_for('userProfile', id=current_user.id))
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data 
            user.email = form.email.data
            db.session.add(user)
            db.session.commit()
            flash('Profile updated')
            return redirect(url_for('userProfile',id=current_user.id))
    return render_template('userprofile.html', user=user, form=form)
