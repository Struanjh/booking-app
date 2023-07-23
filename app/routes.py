from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime, timedelta
import pytz
from app import app, db
from app.forms import LoginForm, RegisterForm, UserProfileForm
from app.models import User, Role, EnglishClasses

@app.route('/')
def home():
    return render_template('index.html', title='Home')  

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.add(user)
            db.session.commit()
            ##Next param contains url user tried to access when redirected from a route protected by login_required
            next_page = request.args.get('next')
            ##Only allow redirects to same domain as this site
            if not next_page or url_parse(next_page).netloc != '':
                return redirect(url_for('home'))
            return redirect(next_page)
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))
    return render_template('login.html', title='Login', form=form)   


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            join_date=datetime.utcnow(),
            oauth=False
        )
        user.role_id=Role.query.filter_by(role='user').first().id
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account successfully created')
        return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)


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
    MAX_STUDENTS = 10
    data = request.get_json()
    classId = int(data['classId'])
    targetClass = EnglishClasses.query.get(classId)
    studentCount = targetClass.students.count()
    state = ''
    if studentCount >= MAX_STUDENTS:
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
    print(current_user.role.role)
    if current_user.role.role == 'admin':
        id = int(request.get('id'))
        user = User.query.filter_by(id=id).first()
        if not user:
            flash('User not found')
            return redirect(url_for('home'))
    else:
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
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data 
            user.email = form.email.data
            db.session.add(user)
            db.session.commit()
            flash('Profile updated')
            return redirect(url_for('userProfile',id=current_user.id))
    return render_template('userprofile.html', user=user, form=form)

    

@app.route('/test')
def test():
    pass
