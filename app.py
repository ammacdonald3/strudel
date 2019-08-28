from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URL'] = ['DATABASE_URL']
db = SQLAlchemy(app)

from models import Result

# Define route for landing page
@app.route('/')
def index():
    return render_template('index.html')

# Define route for page to add recipes
@app.route('/add', methods=['GET','POST'])
def add_recipe():
    output = []
    results = {}
    # If user submits data on input form, write to DB
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
        # Return error if database write was unsuccessful
        except:
            output.append("Item did not add to database :(")
    return render_template('add.html', output=output)

# Define route for page to view all recipes
@app.route('/all_recipes', methods=['GET','POST'])
def all_recipes():
    recipe_list = Result.query.all()
    return render_template("all_recipes.html", recipe_list=recipe_list)

# Define route for page to view detailed info about one recipe
@app.route('/recipe/<recipe_id>')
def recipe_detail(recipe_id):
    recipe = Result.query.filter_by(id=recipe_id).first_or_404()
    return render_template('recipe_detail.html', recipe=recipe)


if __name__ == '__main__':
    app.run()