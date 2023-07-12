from flask import render_template
from app import app

@app.route('/')
def home_route():
    return render_template('index.html', title='Home')  

@app.route('/login')
def login_view():
    return render_template('login_register.html', title='Login')   


    