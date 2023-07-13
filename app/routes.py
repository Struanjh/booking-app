from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm

@app.route('/')
def home_route():
    return render_template('index.html', title='Home')  

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    form = LoginForm()
    if form.validate_on_submit():
        flash('This app received your username: {} and password {}'
        .format(
            form.username.data,
            form.password.data
        ))
        return redirect('/login')
    return render_template('login_register.html', title='Login', form=form)   


    