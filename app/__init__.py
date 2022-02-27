import os
import flask_sqlalchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

login = LoginManager()
login.login_view = 'login'


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)
login.init_app(app)


from app import routes, models

if __name__ == '__main__':
    app.run()
