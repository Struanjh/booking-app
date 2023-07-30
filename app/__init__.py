
from flask import Flask
from config import Config
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_admin import Admin

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
moment = Moment(app)
login = LoginManager(app)
login.login_view = 'auth_bp.login'

from app.auth.routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

#avoid circular imports
from app import routes, models, admin





