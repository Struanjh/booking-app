from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, FloatField
from wtforms.validators import DataRequired, Email
from app.models import User

class UserProfileForm(FlaskForm):
    id = FloatField('User ID')
    join_date = DateTimeField('Join Date')
    last_login = DateTimeField('Last Login')
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    edit_submit = SubmitField('Edit Profile')