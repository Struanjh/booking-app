
from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), index=True, unique=True)
    pw_hash = db.Column(db.String(128))
    join_date = db.Column(db.DateTime, index=True)
    last_login = db.Column(db.DateTime, index=True)
    role = db.Column(db.String(64))
    oauth = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {}>'.format(self.email)


class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Class starts {} and finishes {}>'.format(self.start_time, self.end_time)


