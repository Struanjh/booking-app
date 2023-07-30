from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_required
from app import app, db
from app.forms import UserProfileForm
from app.models import User


@app.route('/')
def home():
    return render_template('index.html', title='Home')  


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
