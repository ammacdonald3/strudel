import os
import flask_sqlalchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
migrate = Migrate()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.add_recipes import bp as add_recipies_bp
    app.register_blueprint(add_recipies_bp)

    from app.view_recipes import bp as view_recipies_bp
    app.register_blueprint(view_recipies_bp)

    from app.meal_planning import bp as meal_planning_bp
    app.register_blueprint(meal_planning_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.food_journal import bp as food_journal_bp
    app.register_blueprint(food_journal_bp)

    return app


from app import models
