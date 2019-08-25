from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URL'] = ['DATABASE_URL']
db = SQLAlchemy(app)

from models import Result

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/<string:name>')
def hello_name(name):
    name = name.capitalize()
    return f"Hello, {name}! Welcome to the site."

@app.route('/all')
def all():
    recipes = ['Steak','Chicken','Veal']
    return render_template('all.html', recipes=recipes)

print(os.environ['APP_SETTINGS'])

if __name__ == '__main__':
    app.run()