from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app import login
from app import db


class App_User(UserMixin, db.Model):
    __tablename__ = 'app_user'

    id = db.Column(db.Integer, primary_key=True)
    app_username = db.Column(db.String(64), index=True, unique=True)
    app_email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    insert_datetime = db.Column(db.DateTime())
    user_recipe = db.relationship('User_Recipe', backref='user_recipe2', lazy=True)
    current_meal = db.relationship('Current_Meal', backref='current_meal2', lazy=True)
    favorite_recipe = db.relationship('Favorite_Recipe', backref='favorite_recipe2', lazy=True)
    recipe = db.relationship('Recipe', backref='recipe', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.app_username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



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
    meal_time = db.Column(db.String())
    recipe_url = db.Column(db.String())
    created_by = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    insert_datetime = db.Column(db.DateTime())
    ingredient = db.relationship('Ingredient', backref='ingredient', lazy=True)
    recipe_step = db.relationship('Recipe_Step', backref='recipe_step', lazy=True)
    user_recipe = db.relationship('User_Recipe', backref='user_recipe1', lazy=True)
    current_meal = db.relationship('Current_Meal', backref='current_meal1', lazy=True)
    favorite_recipe = db.relationship('Favorite_Recipe', backref='favorite_recipe1', lazy=True)


    def __init__(self, recipe_name, recipe_desc, recipe_prep_time, recipe_cook_time, recipe_total_time, serving_size, diet_vegetarian, diet_vegan, diet_gluten, meal_time, recipe_url, created_by, insert_datetime):
        self.recipe_name = recipe_name
        self.recipe_desc = recipe_desc
        self.recipe_prep_time = recipe_prep_time
        self.recipe_cook_time = recipe_cook_time
        self.recipe_total_time = recipe_total_time
        self.serving_size = serving_size
        self.diet_vegetarian = diet_vegetarian
        self.diet_vegan = diet_vegan
        self.diet_gluten = diet_gluten
        self.meal_time = meal_time
        self.recipe_url = recipe_url
        self.created_by = created_by
        self.insert_datetime = insert_datetime

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



class Recipe_Step(db.Model):
    __tablename__ = 'recipe_step'

    recipe_step_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.recipe_id'), nullable=False)
    step_desc = db.Column(db.String())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, recipe_id, step_desc, insert_datetime):
        self.recipe_id = recipe_id
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
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.recipe_id'), nullable=False)
    app_user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    day_number = db.Column(db.Integer())
    active_ind = db.Column(db.Boolean())
    insert_datetime = db.Column(db.DateTime())

    def __init__(self, recipe_id, app_user_id, day_number, active_ind, insert_datetime):
        self.recipe_id = recipe_id
        self.app_user_id = app_user_id
        self.day_number = day_number
        self.active_ind = active_ind
        self.insert_datetime = insert_datetime

    def __repr__(self):
        return '<id {}>'.format(self.current_meal_id)



class LoginForm(FlaskForm):
    app_username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Stay logged in')
    submit = SubmitField('Sign In')



class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    app_username = StringField('Username', validators=[DataRequired()])
    app_email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, app_username):
        app_user = App_User.query.filter_by(app_username=app_username.data).first()
        if app_user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, app_email):
        app_user = App_User.query.filter_by(app_email=app_email.data).first()
        if app_user is not None:
            raise ValidationError('Please use a different email address.')

@login.user_loader
def load_user(id):
    return App_User.query.get(id)