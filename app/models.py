
from app import app, db, login
from time import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for
from flask_login import UserMixin, current_user
import jwt

## ASSOC TABLE TO MANAGE MANY-MANY RELATIONSHIP BETWEEN CLASSES AND USERS
class_bookings = db.Table(
    'class_bookings',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('class_id', db.Integer, db.ForeignKey('english_classes.id'))
)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(64), nullable=False)
    users = db.Relationship('User', backref='role')

    def __repr__(self):
        return '<Role: {}>'.format(self.role)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), index=True, unique=True)
    pw_hash = db.Column(db.String(128))
    join_date = db.Column(db.DateTime, index=True)
    last_login = db.Column(db.DateTime, index=True)
    oauth = db.Column(db.Boolean)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    #ARGS -> 1-other side of many to many relationship. 2-assoc table, 3-reference used for this model from other side of many-many
    classes = db.Relationship(
        'EnglishClasses',
        secondary=class_bookings,
        backref=db.backref('students', lazy='dynamic'),
        lazy='dynamic'
    )
    classes_not_dynamic = db.Relationship(
        'EnglishClasses',
        secondary=class_bookings,
        backref=db.backref('students_not_dynamic'),
        viewonly=True
    )

    def set_password(self, pw):
        self.pw_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.pw_hash, pw)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
        )

    ##Doesn't require class instance to be called
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


    def __repr__(self):
        return '<User {}>'.format(self.email)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class EnglishClasses(db.Model):
    __tablename__ = 'english_classes'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Class ID: {}>'.format(self.id)