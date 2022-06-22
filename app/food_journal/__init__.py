from flask import Blueprint

bp = Blueprint('food_journal', __name__)

from app.food_journal import routes