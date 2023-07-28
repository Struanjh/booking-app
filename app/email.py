from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    print(msg)
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_token(expires_in=60, msg='reset_password')
    ##7200
    send_email('Booking App Team: Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password_email.html',
                                         user=user, token=token)
    )

def send_account_confirmation_email(user):
    token = user.get_token(expires_in=60, msg='confirm_account')
    ##86400
    send_email('Booking App Team: Confirm your email',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/confirm_account_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/confirm_account_email.html',
                                         user=user, token=token)
    )
