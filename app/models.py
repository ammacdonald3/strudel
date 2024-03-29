from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app import db, login
from time import time
from datetime import datetime
import jwt

class App_User(UserMixin, db.Model):
    __tablename__ = 'app_user'

    id = db.Column(db.Integer, primary_key=True)
    app_username = db.Column(db.String(64), index=True, unique=True)
    app_email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    insert_datetime = db.Column(db.DateTime())
    admin = db.Column(db.Boolean())
    google_id = db.Column(db.String)
    native_authenticated = db.Column(db.Boolean())
    google_authenticated = db.Column(db.Boolean())
    last_seen = db.Column(db.DateTime, default=datetime.now)

    user_recipe = db.relationship('User_Recipe', backref='user_recipe2', lazy=True)
    current_meal = db.relationship('Current_Meal', backref='current_meal2', lazy=True)
    favorite_recipe = db.relationship('Favorite_Recipe', backref='favorite_recipe2', lazy=True)
    recipe = db.relationship('Recipe', backref='recipe', lazy=True)
    shopping_list = db.relationship('Shopping_List', backref="shopping_list3", lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.app_email)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return App_User.query.get(id)


class Weekday(db.Model):
    __tablename__ = 'weekday'

    weekday_id = db.Column(db.Integer, primary_key=True)
    weekday_name = db.Column(db.String())
    current_meal = db.relationship('Current_Meal', backref='current_meal', lazy=True)

    def __init__(self, weekday_name):
        self.weekday_name = weekday_name

    def __repr__(self):
        return '<id {}>'.format(self.weekday_id)


class Recipe(db.Model):
    __tablename__ = 'recipe'

    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String())
    recipe_desc = db.Column(db.String())
    recipe_prep_time = db.Column(db.Integer())
    recipe_cook_time = db.Column(db.Integer())
    recipe_total_time = db.Column(db.Integer())
    serving_size = db.Column(db.Integer())
    diet_vegan = db.Column(db.Boolean())
    diet_vegetarian = db.Column(db.Boolean())
    diet_gluten = db.Column(db.Boolean())
    meal_breakfast = db.Column(db.Boolean())
    meal_lunch = db.Column(db.Boolean())
    meal_dinner = db.Column(db.Boolean())
    recipe_url = db.Column(db.String())
    recipe_image_url = db.Column(db.String())
    created_by = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    insert_datetime = db.Column(db.DateTime())
    recipe_deleted = db.Column(db.Boolean())
    editor_certified = db.Column(db.Boolean())
    ingredient = db.relationship('Ingredient', backref='ingredient', lazy=True)
    recipe_step = db.relationship('Recipe_Step', backref='recipe_step', lazy=True)
    user_recipe = db.relationship('User_Recipe', backref='user_recipe1', lazy=True)
    current_meal = db.relationship('Current_Meal', backref='current_meal1', lazy=True)
    favorite_recipe = db.relationship('Favorite_Recipe', backref='favorite_recipe1', lazy=True)
    shopping_list = db.relationship('Shopping_List', backref="shopping_list1", lazy=True)


    def __init__(self, recipe_name, recipe_desc, recipe_prep_time, recipe_cook_time, recipe_total_time, serving_size, diet_vegetarian, diet_vegan, diet_gluten, meal_breakfast, meal_lunch, meal_dinner, recipe_url, recipe_image_url, created_by, insert_datetime, recipe_deleted, editor_certified):
        self.recipe_name = recipe_name
        self.recipe_desc = recipe_desc
        self.recipe_prep_time = recipe_prep_time
        self.recipe_cook_time = recipe_cook_time
        self.recipe_total_time = recipe_total_time
        self.serving_size = serving_size
        self.diet_vegetarian = diet_vegetarian
        self.diet_vegan = diet_vegan
        self.diet_gluten = diet_gluten
        self.meal_breakfast = meal_breakfast
        self.meal_lunch = meal_lunch
        self.meal_dinner = meal_dinner
        self.recipe_url = recipe_url
        self.recipe_image_url = recipe_image_url
        self.created_by = created_by
        self.insert_datetime = insert_datetime
        self.recipe_deleted = recipe_deleted
        self.editor_certified = editor_certified

    def __repr__(self):
        return '<id {}>'.format(self.recipe_id)


class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    ingredient_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.recipe_id'), nullable=False)
    ingredient_desc = db.Column(db.String())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, recipe_id, ingredient_desc, insert_datetime):
        self.recipe_id = recipe_id
        self.ingredient_desc = ingredient_desc
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return 'id {}>'.format(self.ingredient_id)


class Journal_Meal(db.Model):
    __tablename__ = 'journal_meal'

    journal_meal_id = db.Column(db.Integer, primary_key=True)
    app_user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.recipe_id'), nullable=True)
    journal_meal_desc = db.Column(db.String())
    eaten_date = db.Column(db.Date())
    eaten_time = db.Column(db.Time())
    eaten_datetime = db.Column(db.DateTime())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, app_user_id, recipe_id, journal_meal_desc, eaten_date, eaten_time, eaten_datetime, insert_datetime):
        self.app_user_id = app_user_id
        self.recipe_id = recipe_id
        self.journal_meal_desc = journal_meal_desc
        self.eaten_date = eaten_date
        self.eaten_time = eaten_time
        self.eaten_datetime = eaten_datetime
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return 'id {}>'.format(self.journal_meal_id)


class Journal_Ingredient(db.Model):
    __tablename__ = 'journal_ingredient'

    journal_ingredient_id = db.Column(db.Integer, primary_key=True)
    app_user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    journal_meal_id = db.Column(db.Integer(), db.ForeignKey('journal_meal.journal_meal_id'), nullable=True)
    ingredient_id = db.Column(db.Integer(), db.ForeignKey('ingredient.ingredient_id'), nullable=True)
    journal_ingredient_desc = db.Column(db.String())
    eaten_date = db.Column(db.Date())
    eaten_time = db.Column(db.Time())
    eaten_datetime = db.Column(db.DateTime())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, app_user_id, journal_meal_id, ingredient_id, journal_ingredient_desc, eaten_date, eaten_time, eaten_datetime, insert_datetime):
        self.app_user_id = app_user_id
        self.journal_meal_id = journal_meal_id
        self.ingredient_id = ingredient_id
        self.journal_ingredient_desc = journal_ingredient_desc
        self.eaten_date = eaten_date
        self.eaten_time = eaten_time
        self.eaten_datetime = eaten_datetime
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return 'id {}>'.format(self.journal_meal_id)


class Journal_Symptom(db.Model):
    __tablename__ = 'journal_symptom'

    journal_symptom_id = db.Column(db.Integer, primary_key=True)
    journal_symptom_desc = db.Column(db.String())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, journal_symptom_desc, insert_datetime):
        self.journal_symptom_desc = journal_symptom_desc
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return 'id {}>'.format(self.journal_symptom_id)


class Journal_Symptom_Severity(db.Model):
    __tablename__ = 'journal_symptom_severity'

    journal_symptom_sev_id = db.Column(db.Integer, primary_key=True)
    journal_symptom_sev_desc = db.Column(db.String())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, journal_symptom_sev_desc, insert_datetime):
        self.journal_symptom_sev_desc = journal_symptom_sev_desc
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return 'id {}>'.format(self.journal_symptom_sev_id)


class Bristol_Scale(db.Model):
    __tablename__ = 'bristol_scale'

    bristol_scale_id = db.Column(db.Integer, primary_key=True)
    bristol_scale_desc = db.Column(db.String())
    bristol_scale_number = db.Column(db.Integer())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, bristol_scale_desc, bristol_scale_number, insert_datetime):
        self.bristol_scale_desc = bristol_scale_desc
        self.bristol_scale_number = bristol_scale_number
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return 'id {}>'.format(self.bristol_scale_id)


class User_Symptom(db.Model):
    __tablename__ = 'user_symptom'

    user_symptom_id = db.Column(db.Integer, primary_key=True)
    app_user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    journal_symptom_id = db.Column(db.Integer(), db.ForeignKey('journal_symptom.journal_symptom_id'), nullable=False)
    bristol_scale_id = db.Column(db.Integer(), db.ForeignKey('bristol_scale.bristol_scale_id'), nullable=True)
    user_symptom_date = db.Column(db.Date())
    user_symptom_time = db.Column(db.Time())
    user_symptom_datetime = db.Column(db.DateTime())
    user_symptom_notes = db.Column(db.String())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, journal_symptom_desc, insert_datetime):
        self.journal_symptom_desc = journal_symptom_desc
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return 'id {}>'.format(self.user_symptom_id)


class User_Link(db.Model):
    __tablename__ = 'user_link'

    user_link_id = db.Column(db.Integer, primary_key=True)
    app_user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    combined_user_id = db.Column(db.String())

    def __init__(self, app_user_id, combined_user_id):
        self.app_user_id = app_user_id
        self.combined_user_id = combined_user_id

    def __repr__(self):
        return 'id {}>'.format(self.user_link_id)
    

class Recipe_Step(db.Model):
    __tablename__ = 'recipe_step'

    recipe_step_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.recipe_id'), nullable=False)
    step_order = db.Column(db.Integer())
    step_desc = db.Column(db.String())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, recipe_id, step_order, step_desc, insert_datetime):
        self.recipe_id = recipe_id
        self.step_order = step_order
        self.step_desc = step_desc
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return 'id {}>'.format(self.recipe_step_id)



class User_Recipe(db.Model):
    __tablename__ = 'user_recipe'

    user_recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.recipe_id'), nullable=False)
    app_user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    user_rating = db.Column(db.Integer())
    owner_ind = db.Column(db.Boolean())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, recipe_id, app_user_id, user_rating, owner_ind, insert_datetime):
        self.recipe_id = recipe_id
        self.app_user_id = app_user_id
        self.user_rating = user_rating
        self.owner_ind = owner_ind
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return '<id {}>'.format(self.user_recipe_id)


class Favorite_Recipe(db.Model):
    __tablename__ = 'favorite_recipe'

    favorite_recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.recipe_id'), nullable=False)
    app_user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    owner_ind = db.Column(db.Boolean())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, recipe_id, app_user_id, owner_ind, insert_datetime):
        self.recipe_id = recipe_id
        self.app_user_id = app_user_id
        self.owner_ind = owner_ind
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return '<id {}>'.format(self.favorite_recipe_id)


class Current_Meal(db.Model):
    __tablename__ = 'current_meal'

    current_meal_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.recipe_id'), nullable=True)
    app_user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    combined_user_id = db.Column(db.String())
    day_number = db.Column(db.Integer())
    meal = db.Column(db.String())
    weekday_id = db.Column(db.Integer(), db.ForeignKey('weekday.weekday_id'), nullable=True)
    active_ind = db.Column(db.Boolean())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, recipe_id, app_user_id, combined_user_id, day_number, meal, weekday_id, active_ind, insert_datetime):
        self.recipe_id = recipe_id
        self.app_user_id = app_user_id
        self.combined_user_id = combined_user_id
        self.day_number = day_number
        self.meal = meal
        self.weekday_id = weekday_id
        self.active_ind = active_ind
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return '<id {}>'.format(self.current_meal_id)


class Shopping_List(db.Model):
    __tablename__ = 'shopping_list'

    shopping_list_id = db.Column(db.Integer, primary_key=True)
    item_desc = db.Column(db.String())
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.recipe_id'), nullable=True)
    ingredient_id = db.Column(db.Integer(), nullable=True)
    app_user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    combined_user_id = db.Column(db.String())
    item_sort = db.Column(db.Integer)
    checked_status = db.Column(db.Boolean())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, item_desc, recipe_id, ingredient_id, app_user_id, combined_user_id, item_sort, checked_status, insert_datetime):
        self.item_desc = item_desc
        self.recipe_id = recipe_id
        self.ingredient_id = ingredient_id
        self.app_user_id = app_user_id
        self.combined_user_id = combined_user_id
        self.item_sort = item_sort
        self.checked_status = checked_status
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return '<id {}>'.format(self.shopping_list_id)


class App_Error(db.Model):
    __tablename__ = 'app_error'

    error_id = db.Column(db.Integer, primary_key=True)
    app_user_id = db.Column(db.Integer())
    insert_datetime = db.Column(db.DateTime())
    error_val = db.Column(db.String())

    def __init__(self, app_user_id, insert_datetime, error_val):
        self.app_user_id = app_user_id
        self.insert_datetime = insert_datetime
        self.error_val = error_val
        
    def __repr__(self):
        return '<id {}>'.format(self.error_id)


@login.user_loader
def load_user(id):
    return App_User.query.get(id)