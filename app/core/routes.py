from flask import render_template, flash, redirect, url_for, request, session, Blueprint
from flask_login import current_user, login_required
from app import db
from app.models import User
from app.core.forms import UserProfileForm
import pytz

core_bp = Blueprint('core_bp', __name__, template_folder='templates/core')

@core_bp.route('/')
def home():
    return render_template('index.html', title='Home')  


@core_bp.route('/userprofile', methods=['GET', 'POST'])
@login_required
def userProfile():
    form = UserProfileForm()
    if form.validate_on_submit():
        form_email = form.email.data.lower()
        email_in_use = User.query.filter_by(email=form_email).first()
        if email_in_use and form_email != current_user.email:
            form.email.errors.append('This email is already in use. Please select a different email')
            return render_template('userprofile.html', title='My Profile', user=current_user, form=form)
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data 
        current_user.email = form_email
        db.session.add(current_user)
        db.session.commit()
        flash('Profile updated')
        return redirect(url_for('core_bp.userProfile',id=current_user.id))
    elif request.method == 'GET':
        form.id.data = current_user.id
        form.join_date.data = current_user.join_date
        form.last_login.data = current_user.last_login
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    return render_template('userprofile.html', user=current_user, title='My Profile', form=form, alert_status='alert-success')
