from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from app import db


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String())
    recipe_desc = db.Column(db.String())
    recipe_prep_time = db.Column(db.Integer())
    recipe_cook_time = db.Column(db.Integer())
    ingredients = db.relationship('Ingredient', backref='recipes', lazy=True)
    steps = db.relationship('Step', backref='steps', lazy=True)


    def __init__(self, recipe_name, recipe_desc, recipe_prep_time, recipe_cook_time):
        self.recipe_name = recipe_name
        self.recipe_desc = recipe_desc
        self.recipe_prep_time = recipe_prep_time
        self.recipe_cook_time = recipe_cook_time

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipes.id'), nullable=False)
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


class Step(db.Model):
    __tablename__ = 'steps'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer(), db.ForeignKey('recipes.id'), nullable=False)
    step_order = db.Column(db.Integer())
    step_desc = db.Column(db.String())

    def __init__(self, recipe_id, step_order, step_desc):
        self.recipe_id = recipe_id
        self.step_order = step_order
        self.step_desc = step_desc

    def __repr__(self):
        return 'id {}>'.format(self.id)