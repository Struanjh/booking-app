from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime, timedelta
import pytz
from app import app, db
from app.forms import LoginForm, RegisterForm
from app.models import User, Role, EnglishClasses

@app.route('/')
@login_required
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
            ##Handle next query param passed when user has been redirected from a route protected by login_required
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
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            join_date=datetime.utcnow,
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
def bookings():
    classes = EnglishClasses.query.all()
    return render_template('bookings.html', title='Bookings', classes=classes)
    
    def nextTenDates(numdays):
        dayOne = datetime.now(pytz.timezone('Asia/Seoul'))
        date_range = [dayOne - timedelta(days=x) for x in range(numdays)]
        print(dayOne, date_range)

    def getMinMaxUtc():
        pass

    