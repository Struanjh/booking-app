import secrets
import requests
from urllib.parse import urlencode
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import User, Role, EnglishClasses
from app.auth.email import send_password_reset_email, send_account_confirmation_email
from app.auth.forms import LoginForm, RegisterForm, UserRequestForm, ResetPasswordForm
from app.auth.password_policy import pw_policy
from flask import Blueprint

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.account_email_verified:
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
        elif user and user.check_password(form.password.data) and not user.account_email_verified:
            flash('Please check your email inbox. You need to verify your account to login. Didn\'t receive the email or link expired? Submit your email below to receive another a new link')
            return redirect(url_for('auth_bp.account_confirmation'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('auth_bp.login'))
    return render_template('login.html', title='Login', form=form)   


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        if not User.validate_password(form.password.data):
            for requirement in pw_policy.test_password(form.password.data):
                alert = f"{requirement.name} password requirement was not satisfied. Must be {requirement.requirement}"
                flash(alert)
                return redirect(url_for('auth_bp.register'))
        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            join_date=datetime.utcnow(),
            oauth=False,
            account_email_verified=False,
            pw_last_set=datetime.utcnow()
        )
        user.role_id=Role.query.filter_by(role='user').first().id
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_account_confirmation_email(user)
        flash('Please check your email inbox. You need to verify your account to login')
        return redirect(url_for('auth_bp.login'))
    return render_template('register.html', title='Register', form=form)


@auth_bp.route('/account_confirmation_request', methods=['GET', 'POST'])
def account_confirmation():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = UserRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_account_confirmation_email(user)
        flash('Please check your email inbox. You need to verify your account to login')
        return redirect(url_for('auth_bp.login'))
    return render_template('account_confirm_request.html',
                           title='Confirm Account', form=form)
   


@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = UserRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.account_email_verified and not user.oauth:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth_bp.login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    ##Static method so can be called directly from the class
    user = User.verify_token(token, msg='reset_password')
    if not user:
        flash('Reset Token invalid. Please submit your email to receive a new link')
        return redirect(url_for('auth_bp.reset_password_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if not User.validate_password(form.password.data):
            for requirement in pw_policy.test_password(form.password.data):
                alert = f"{requirement.name} password requirement was not satisfied. Must be {requirement.requirement}"
            flash(alert)
            return redirect(url_for('auth_bp.reset_password', token=token))
        user.set_password(form.password.data)
        user.pw_last_set = datetime.utcnow()
        db.session.commit()
        flash('Your password has been reset. Please login with your new password')
        return redirect(url_for('auth_bp.login'))
    return render_template('reset_password.html', form=form)


@auth_bp.route('/confirm_account/<token>')
def confirm_account(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_token(token, msg='confirm_account')
    if not user:
        flash('Reset Token invalid. Please submit your email to receive a new link')
        return redirect(url_for('auth_bp.account_confirmation'))
    user.account_email_verified=True
    db.session.add(user)
    db.session.commit()
    flash('Your account has been verified. Please login with your email and password')
    return redirect(url_for('auth_bp.login'))


##Initiate oauth process by redirecting app to oauth providers authorization endpoint
@auth_bp.route('/authorize/<provider>')
def oauth2_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('home'))
    
    ##Select relevant oauth provider from config dictionary
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)
    
    # generate a random string for the state parameter
    session['oauth2_state'] = secrets.token_urlsafe(16)

    ## Prepare query params then redirect user to the Oauth provider auth endpoint
    params = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('auth_bp.oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    # redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_data['authorize_url'] + '?' + params)


##Process reponse from oauth provider, login and create user if needed
@auth_bp.route('/callback/<provider>')
def oauth2_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('home'))
    
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    def validateProviderRes():
        # if there was an authentication error, flash the error messages and exit
        if 'error' in request.args:
            for k, v in request.args.items():
                if k.startswith('error'):
                    flash(f'{k}: {v}')
            return redirect(url_for('home'))
        # make sure that the state parameter matches the one created in the authorization request
        if request.args['state'] != session.get('oauth2_state'):
            abort(401)
        # make sure that the authorization code is present
        if 'code' not in request.args:
            abort(401)
    
    def getAccessToken():
        # Make a POST req to oauth provider to exhcange auth code for access token
        response = requests.post(
            provider_data['token_url'], 
            data = {
                'client_id': provider_data['client_id'],
                'client_secret': provider_data['client_secret'],
                'code': request.args['code'],
                'grant_type': 'authorization_code',
                'redirect_uri': url_for('auth_bp.oauth2_callback', provider=provider,
                                        _external=True),
            },
            headers={'Accept': 'application/json'}
        )
        if response.status_code != 200:
            abort(401)
        oauth2_token = response.json().get('access_token')
        if not oauth2_token:
            abort(401)
        return oauth2_token
    

    def getUserDetails():
        # GET req to oauth provider to retrieve user details
        response = requests.get(provider_data['userinfo']['url'], headers={
            'Authorization': 'Bearer ' + oauth2_token,
            'Accept': 'application/json',
        })
        if response.status_code != 200:
            abort(401)
        return response.json()


    def updateDB():
        first_name = userInfo['given_name']
        last_name = userInfo['family_name']
        email = userInfo['email'].lower()
        oauth_user = User.query.filter_by(email=email).first()

        ##Check in case user has already registered with that email as regular user
        if oauth_user and oauth_user.oauth == False:
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
                role_id = Role.query.filter_by(role='user').first().id,
                account_email_verified=True,
                pw_last_set=None
            )

        oauth_user.last_login = datetime.utcnow()
        db.session.add(oauth_user)
        db.session.commit()
        login_user(oauth_user)
    
    validateProviderRes()
    oauth2_token = getAccessToken()
    userInfo = getUserDetails()
    updateDB()
    return redirect(url_for('home'))
