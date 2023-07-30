
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
from app.booking.routes import booking_bp
from app.core.routes import core_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(booking_bp)
app.register_blueprint(core_bp)

#avoid circular imports
from app import models, admin, routes





