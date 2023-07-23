
from flask import Flask
from config import Config
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
login = LoginManager(app)
login.login_view = 'login'

# from flask_admin.contrib.sqla import ModelView
# from flask_admin import Admin, AdminIndexView

# class MyAdminIndexView(AdminIndexView):
#     def is_accessible(self):
#         return current_user.role.role == 'admin'
    
#     def inaccessible_callback(self, name, **kwargs):
#         return redirect(url_for('home'))

# admin = Admin(app, index_view=MyAdminIndexView())
# admin.add_view(ModelView(models.User, db.session))

#avoid circular imports
from app import routes, models



