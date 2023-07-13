from flask import render_template
from app import app
from app.forms import LoginForm

@app.route('/')
def home_route():
    return render_template('index.html', title='Home')  

@app.route('/login')
def login_view():
    form = LoginForm()
    return render_template('login_register.html', title='Login', form=form)   


    