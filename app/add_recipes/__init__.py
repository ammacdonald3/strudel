from flask import Blueprint

bp = Blueprint('add_recipes', __name__)

from app.add_recipes import routes