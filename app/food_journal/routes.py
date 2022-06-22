from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort, send_from_directory, current_app
import flask_sqlalchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
from sqlalchemy import or_, func
import random
import sys

from flask import current_app as app

from app import db

from app.models import Recipe, Ingredient, Recipe_Step, App_User, Current_Meal, User_Recipe, Favorite_Recipe, Shopping_List, App_Error

from app.food_journal import bp

# Define route for view food journal page
@bp.route('/view_food_journal', methods=['GET', 'POST'])
@login_required
def view_food_journal():
    output = []

    return render_template('food_journal/view_food_journal.html', output=output)