import click, os, time
import pytz
from app import db
from app.models import EnglishClasses
from datetime import datetime, timedelta, timezone
from flask import session


def register(app):        
    @app.cli.command()
    def addclass():
        """Add Classes to DB at scheduled interval"""
        open_in_days = app.config['CLASSES_OPEN_IN_DAYS']
        delta = timedelta(days=+open_in_days)
        classDate = datetime.now(pytz.timezone(app.config['TZ_INFO'])) + delta
        for dailyClass in app.config['DAILY_CLASS_SCHEDULE']:
            d_class = app.config['DAILY_CLASS_SCHEDULE'][dailyClass]
            s_hour, s_minute = d_class['start_time'].split(".")
            e_hour, e_minute = d_class['end_time'].split(".")
            newClass = EnglishClasses()
            newClass.start_time = datetime(
                year=classDate.year, 
                month=classDate.month,
                day=classDate.day, 
                hour=int(s_hour),
                minute=int(s_minute),
                tzinfo = pytz.timezone(app.config['TZ_INFO'])
            )
            newClass.end_time = datetime(
                year=classDate.year, 
                month=classDate.month,
                day=classDate.day, 
                hour=int(e_hour),
                minute=int(e_minute),
                tzinfo = pytz.timezone(app.config['TZ_INFO'])
            )
            print(newClass.start_time)
            print(newClass.end_time)
            print('Class Added!')
            db.session.add(newClass)
        db.session.commit()
        print('DONE!')






