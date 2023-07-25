import pytz
import secrets
import requests
from urllib.parse import urlencode
from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
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
            email=form.email.data.lower(),
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

##Initiate oauth process by redirecting app to oauth providers authorization endpoint
@app.route('/authorize/<provider>')
def oauth2_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    
    ##Select relevant oauth provider from config dictionary
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)
    
    # generate a random string for the state parameter
    session['oauth2_state'] = secrets.token_urlsafe(16)

    ## Prepare query params then redirect user to the Oauth provider auth endpoint
    params = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    # redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_data['authorize_url'] + '?' + params)

##Process reponse from oauth provider, login and create user if needed
@app.route('/callback/<provider>')
def oauth2_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)
    
    # if there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('index'))

    # make sure that the state parameter matches the one created in the authorization request
    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    # make sure that the authorization code is present
    if 'code' not in request.args:
        abort(401)
    
     # Make a POST req to oauth provider to exhcange auth code for access token
    response = requests.post(
        provider_data['token_url'], 
        data = {
            'client_id': provider_data['client_id'],
            'client_secret': provider_data['client_secret'],
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('oauth2_callback', provider=provider,
                                    _external=True),
        },
        headers={'Accept': 'application/json'}
    )

    if response.status_code != 200:
        abort(401)

    oauth2_token = response.json().get('access_token')
    print(oauth2_token)

    if not oauth2_token:
        abort(401)
    
    # GET req to oauth provider to retrieve users email address
    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    res_data = response.json()
    print(res_data)
    first_name = res_data['given_name']
    last_name = res_data['family_name']
    email = res_data['email'].lower()
    print(first_name, last_name, email)
    # email = provider_data['userinfo']['email'](response.json())
    # print(email)
    
    # ##Find current user
    oauth_user = User.query.filter_by(email=email).first()
    print('Oauth User...')
    print(oauth_user)

    ##Check in case user has already registered with that email as regular user
    if oauth_user and oauth_user.oauth == False:
        print("USER ALREADY REGISTERED WITH REGULAR ACCOUNT")
        flash(f'You have already registered the email {email}. Please login with your email and password')
        return redirect(url_for('home'))

    ##First time user so create record
    if not oauth_user:
        oauth_user = User(
            first_name = first_name,
            last_name = last_name,
            email = email,
            pw_hash = None,
            join_date = datetime.utcnow(),
            oauth = True,
            role_id = Role.query.filter_by(role='user').first().id
        )
        print("NEW ACCOUNT WOULD JUST HAVE BEEN CREATED")
    oauth_user.last_login = datetime.utcnow()
    print("USER READY TO BE LOGGED IN....")
    db.session.add(oauth_user)
    db.session.commit()
    login_user(oauth_user)
    return redirect(url_for('home'))