from flask import Flask, render_template, current_app
from google.oauth2 import id_token
from google.auth.transport import requests

from flask import current_app as app

from app import db

from app.models import Recipe, Ingredient, Recipe_Step, App_User, Current_Meal, User_Recipe, Favorite_Recipe, Shopping_List, App_Error

from app.main import bp

# Define route for landing page
@bp.route('/')
def index():
    google_login_uri = current_app.config['GOOGLE_LOGIN_URI']
    google_client_id = current_app.config['GOOGLE_CLIENT_ID']
    return render_template('main/index.html', google_login_uri=google_login_uri, google_client_id=google_client_id)



    

