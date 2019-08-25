from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from app import db


class Result(db.Model):
    __tablename__ = 'recipes'

    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String())
    recipe_desc = db.Column(db.String())
    recipe_prep_time = db.Column(db.Integer())
    recipe_cook_time = db.Column(db.Integer())


    def __init__(self, recipe_name, recipe_desc, recipe_prep_time, recipe_cook_time):
        self.recipe_name = recipe_name
        self.recipe_desc = recipe_desc
        self.recipe_prep_time = recipe_prep_time
        self.recipe_cook_time = recipe_cook_time

    def __repr__(self):
        return '<id {}>'.format(self.id)

