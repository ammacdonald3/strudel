from flask import Blueprint

bp = Blueprint('view_recipes', __name__)

from app.view_recipes import routes