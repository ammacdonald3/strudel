from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URL'] = ['DATABASE_URL']
db = SQLAlchemy(app)

from models import Result

@app.route('/')
def hello():
    return render_template('index.html')



@app.route('/add', methods=['GET','POST'])
def add_recipe():
    output = []
    results = {}
    if request.method == "POST":
        try:
            result = Result(
                recipe_name=request.form['recipe_name'],
                recipe_desc=request.form['recipe_desc'],
                recipe_prep_time=request.form['recipe_prep_time'],
                recipe_cook_time=request.form['recipe_cook_time']
            )
            db.session.add(result)
            db.session.commit()
            output.append("Item successfully added!")
        except:
            output.append("Item did not add to database :(")
    return render_template('add.html', output=output)

@app.route('/all')
def all():
    recipes = ['Steak','Chicken','Veal']
    return render_template('all.html', recipes=recipes)


if __name__ == '__main__':
    app.run()