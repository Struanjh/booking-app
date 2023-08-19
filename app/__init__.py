
import logging, os
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import config
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

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    ##Invoking static method from config class - currently doesn't do anything - but could allow more complext configurations to be performed
    config[config_name].init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    moment.init_app(app)
    login.init_app(app)
    admin.init_app(app)
    from app.auth.routes import auth_bp
    from app.booking.routes import booking_bp
    from app.core.routes import core_bp
    from app.errors.handlers import errors_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(booking_bp)
    app.register_blueprint(core_bp)
    app.register_blueprint(errors_bp)
    #Enable debugging logging for prod
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/booking_app.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            )
        )
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.ERROR)
        app.logger.info('Booking App startup')
    return app

#avoid circular imports
from app import models, admins





