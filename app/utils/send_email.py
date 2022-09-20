from flask_mail import Message
from app import mail
from flask import current_app
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    print('---------MSG----------')
    print(msg)
    print(msg.body)
    print(msg.html)
    msg.body = text_body
    msg.html = html_body
    print('---------MSG----------')
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()