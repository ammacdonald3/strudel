from flask import Flask, render_template, current_app
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from sqlalchemy.sql import func

from flask import current_app as app

from app import db

from app.models import Recipe, Ingredient, Recipe_Step, App_User, Current_Meal, User_Recipe, Favorite_Recipe, Shopping_List, App_Error

from app.admin import bp

# Define route for admin page
@bp.route('/admin')
@login_required
def admin():

    google_login_uri = current_app.config['GOOGLE_LOGIN_URI']
    google_client_id = current_app.config['GOOGLE_CLIENT_ID']

    admins = (db.session.query(App_User).filter_by(admin=True).all())
    admins_list = [r.id for r in admins]
    if (current_user.id in admins_list):
        current_user_admin = True

        # Get list of users
        user_list = (db.session.query(
            App_User.app_email,
            func.to_char(App_User.last_seen, 'YYYY-MM-DD').label('last_seen'),
            func.to_char(App_User.insert_datetime, 'YYYY-MM-DD').label('insert_date'),
            App_User.first_name,
            App_User.last_name,
            App_User.admin,
            App_User.native_authenticated,
            App_User.google_authenticated
            ) \
            .order_by(func.to_char(App_User.last_seen, 'YYYY-MM-DD').desc())
            )
    
    else:
        current_user_admin = False

        user_list = None


    return render_template('admin/admin.html', user_list=user_list, google_login_uri=google_login_uri, google_client_id=google_client_id, current_user_admin=current_user_admin)


    




    

