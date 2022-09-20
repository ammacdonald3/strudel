from flask import render_template, current_app
from app.utils.send_email import send_email

def send_password_reset_email(app_user):
    token = app_user.get_reset_password_token()
    print('-------TOKEN--------')
    print(token)
    print('-------TOKEN--------')
    send_email('[Strudel] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[app_user.app_email],
               text_body=render_template('email_templates/reset_password.txt',
                                         app_user=app_user, token=token),
               html_body=render_template('email_templates/reset_password.html',
                                         app_user=app_user, token=token))


