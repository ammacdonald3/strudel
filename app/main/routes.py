from flask import Flask, render_template, current_app
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests

from flask import current_app as app

from app import db

from app.models import Recipe, Ingredient, Recipe_Step, App_User, Current_Meal, User_Recipe, Favorite_Recipe, Shopping_List, App_Error

from app.main import bp

# Update the last_seen field every time the user performs an action
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.flush()
        db.session.commit()


# Define route for landing page
@bp.route('/')
def index():
    google_login_uri = current_app.config['GOOGLE_LOGIN_URI']
    google_client_id = current_app.config['GOOGLE_CLIENT_ID']

    # Identify if the current user is an administrator
    admins = (db.session.query(App_User).filter_by(admin=True).all())
    admins_list = [r.id for r in admins]

    if current_user.is_authenticated:
        if (current_user.id in admins_list):
            current_user_admin = True
        
        else:
            current_user_admin = False
            
    else:
        current_user_admin = False


    return render_template('main/index.html', google_login_uri=google_login_uri, google_client_id=google_client_id, current_user_admin=current_user_admin)



    

