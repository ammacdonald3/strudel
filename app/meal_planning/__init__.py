from flask import Blueprint

bp = Blueprint('meal_planning', __name__)

from app.meal_planning import routes