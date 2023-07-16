
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(64), nullable=False)
    users = db.Relationship('User', backref='role')

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

    def __repr__(self):
        return '<User {}>'.format(self.email)
        
    def set_password(self, pw):
        self.pw_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.pw_hash, pw)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Classes(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Class starts {} and finishes {}>'.format(self.start_time, self.end_time)

