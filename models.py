from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app import login
from app import db


class Recipe(db.Model):
    __tablename__ = 'recipe'

    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String())
    recipe_desc = db.Column(db.String())
    recipe_prep_time = db.Column(db.Integer())
    recipe_cook_time = db.Column(db.Integer())
    serving_size = db.Column(db.Integer())
    diet_vegetarian = db.Column(db.String())
    diet_vegan = db.Column(db.Boolean())
    diet_gluten = db.Column(db.String())
    meal_time = db.Column(db.String())
    ingredient = db.relationship('Ingredient', backref='recipe', lazy=True)
    recipe_step = db.relationship('Recipe_Step', backref='recipe_step', lazy=True)
    user_recipe = db.relationship('User_Recipe', backref='user_recipe', lazy=True)


    def __init__(self, recipe_name, recipe_desc, recipe_prep_time, recipe_cook_time, serving_size, diet_vegetarian, diet_vegan, diet_gluten, meal_time):
        self.recipe_name = recipe_name
        self.recipe_desc = recipe_desc
        self.recipe_prep_time = recipe_prep_time
        self.recipe_cook_time = recipe_cook_time
        self.serving_size = serving_size
        self.diet_vegetarian = diet_vegetarian
        self.diet_vegan = diet_vegan
        self.diet_gluten = diet_gluten
        self.meal_time = meal_time

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.id'), nullable=False)
    ingredient_qty = db.Column(db.Integer())
    ingredient_measurement = db.Column(db.String())
    ingredient_desc = db.Column(db.String())

    def __init__(self, recipe_id, ingredient_qty, ingredient_measurement, ingredient_desc):
        self.recipe_id = recipe_id
        self.ingredient_qty = ingredient_qty
        self.ingredient_measurement = ingredient_measurement
        self.ingredient_desc = ingredient_desc

    def __repr__(self):
        return 'id {}>'.format(self.id)


class Recipe_Step(db.Model):
    __tablename__ = 'recipe_step'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.id'), nullable=False)
    step_desc = db.Column(db.String())

    def __init__(self, recipe_id, step_desc):
        self.recipe_id = recipe_id
        self.step_desc = step_desc

    def __repr__(self):
        return 'id {}>'.format(self.id)


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class User_Recipe(db.Model):
    __tablename__ = 'user_recipe'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    user_rating = db.Column(db.String())
    owner_ind = db.Column(db.String())

    def __init__(self, recipe_id, user_id, user_rating, owner_ind):
        self.recipe_id = recipe_id
        self.user_id = user_id
        self.user_rating = user_rating
        self.owner_ind = owner_ind

    def __repr__(self):
        return '<id {}>'.format(self.id)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

@login.user_loader
def load_user(id):
    return User.query.get(id)