from app import app

@app.route('/')
def home_route():
    return '<h1>Welcome to the home page</h1>'

@app.route('/login')
def login_view():
    return '<h2>Please login or register</h2>'