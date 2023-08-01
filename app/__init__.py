
from flask import Flask
from config import Config
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_admin import Admin

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
moment = Moment()
login = LoginManager()
admin = Admin()
login.login_view = 'auth_bp.login'
login.login_message = 'Please login to view this page'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    moment.init_app(app)
    login.init_app(app)
    admin.init_app(app)
    from app.auth.routes import auth_bp
    from app.booking.routes import booking_bp
    from app.core.routes import core_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(booking_bp)
    app.register_blueprint(core_bp)
    return app

#avoid circular imports
from app import models, admins





