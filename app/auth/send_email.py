from flask_mail import Message
from app import mail
from flask import render_template, current_app
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(app_user):
    token = app_user.get_reset_password_token()
    send_email('[Strudel] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[app_user.app_email],
               text_body=render_template('email_templates/reset_password.txt',
                                         app_user=app_user, token=token),
               html_body=render_template('email_templates/reset_password.html',
                                         app_user=app_user, token=token))


