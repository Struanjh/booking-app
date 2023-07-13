from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route('/')
def home():
    return render_template('index.html', title='Home')  

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('This app received your username: {} and password {}'
        .format(
            form.username.data,
            form.password.data
        ))
        return redirect(url_for('login'))
    return render_template('login_register.html', title='Login', form=form)   


    