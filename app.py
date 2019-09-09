from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URL'] = ['DATABASE_URL']
db = SQLAlchemy(app)

from models import Recipe, Ingredient, Step


# Define route for landing page
@app.route('/')
def index():
    return render_template('index.html')


# Define route for page to add recipes
@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    output = []
    # If user submits data on input form, write to DB
    if request.method == "POST":
        # Write recipe info
        try:
            recipe = Recipe(
                recipe_name=request.form['recipe_name'],
                recipe_desc=request.form['recipe_desc'],
                recipe_prep_time=request.form['recipe_prep_time'],
                recipe_cook_time=request.form['recipe_cook_time']
            )
            db.session.add(recipe)
            db.session.flush()
            db.session.commit()
            output.append("Recipe successfully added!")
        # Return error if database write was unsuccessful
        except:
            output.append("Recipe did not add to database :(")

        # Write Ingredient 1
        try:
            ingredient1 = Ingredient(
                # ingredient_qty=request.form('ingredient_qty')
                recipe_id=recipe.id,
                ingredient_qty=request.form['ingredient_qty1'],
                ingredient_measurement=request.form['ingredient_measurement1'],
                ingredient_desc=request.form['ingredient_desc1']
            )
            db.session.add(ingredient1)
            db.session.commit()
        # Return error if database write was unsuccessful
        except:
            output.append("Ingredient 1 did not add to database :(")

        # Write Ingredient 2
        try:
            ingredient2 = Ingredient(
                # ingredient_qty=request.form('ingredient_qty')
                recipe_id=recipe.id,
                ingredient_qty=request.form['ingredient_qty2'],
                ingredient_measurement=request.form['ingredient_measurement2'],
                ingredient_desc=request.form['ingredient_desc2']
            )
            db.session.add(ingredient2)
            db.session.commit()
        # Return error if database write was unsuccessful
        except:
            output.append("Ingredient2 did not add to database :(")

        # Write Ingredient 3
        try:
            ingredient3 = Ingredient(
                # ingredient_qty=request.form('ingredient_qty')
                recipe_id=recipe.id,
                ingredient_qty=request.form['ingredient_qty3'],
                ingredient_measurement=request.form['ingredient_measurement3'],
                ingredient_desc=request.form['ingredient_desc3']
            )
            db.session.add(ingredient3)
            db.session.commit()
        # Return error if database write was unsuccessful
        except:
            output.append("Ingredient3 did not add to database :(")

            # Write Ingredient 4
            try:
                ingredient4 = Ingredient(
                    # ingredient_qty=request.form('ingredient_qty')
                    recipe_id=recipe.id,
                    ingredient_qty=request.form['ingredient_qty4'],
                    ingredient_measurement=request.form['ingredient_measurement4'],
                    ingredient_desc=request.form['ingredient_desc4']
                )
                db.session.add(ingredient4)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Ingredient4 did not add to database :(")

            # Write Ingredient 5
            try:
                ingredient5 = Ingredient(
                    # ingredient_qty=request.form('ingredient_qty')
                    recipe_id=recipe.id,
                    ingredient_qty=request.form['ingredient_qty5'],
                    ingredient_measurement=request.form['ingredient_measurement5'],
                    ingredient_desc=request.form['ingredient_desc5']
                )
                db.session.add(ingredient5)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Ingredient5 did not add to database :(")

            # Write Ingredient 6
            try:
                ingredient6 = Ingredient(
                    # ingredient_qty=request.form('ingredient_qty')
                    recipe_id=recipe.id,
                    ingredient_qty=request.form['ingredient_qty6'],
                    ingredient_measurement=request.form['ingredient_measurement6'],
                    ingredient_desc=request.form['ingredient_desc6']
                )
                db.session.add(ingredient6)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Ingredient6 did not add to database :(")

            # Write Ingredient 7
            try:
                ingredient7 = Ingredient(
                    # ingredient_qty=request.form('ingredient_qty')
                    recipe_id=recipe.id,
                    ingredient_qty=request.form['ingredient_qty7'],
                    ingredient_measurement=request.form['ingredient_measurement7'],
                    ingredient_desc=request.form['ingredient_desc7']
                )
                db.session.add(ingredient7)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Ingredient7 did not add to database :(")

            # Write Ingredient 8
            try:
                ingredient8 = Ingredient(
                    # ingredient_qty=request.form('ingredient_qty')
                    recipe_id=recipe.id,
                    ingredient_qty=request.form['ingredient_qty8'],
                    ingredient_measurement=request.form['ingredient_measurement8'],
                    ingredient_desc=request.form['ingredient_desc8']
                )
                db.session.add(ingredient8)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Ingredient8 did not add to database :(")

            # Write Ingredient 9
            try:
                ingredient9 = Ingredient(
                    # ingredient_qty=request.form('ingredient_qty')
                    recipe_id=recipe.id,
                    ingredient_qty=request.form['ingredient_qty9'],
                    ingredient_measurement=request.form['ingredient_measurement9'],
                    ingredient_desc=request.form['ingredient_desc9']
                )
                db.session.add(ingredient9)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Ingredient9 did not add to database :(")

            # Write Ingredient 10
            try:
                ingredient10 = Ingredient(
                    # ingredient_qty=request.form('ingredient_qty')
                    recipe_id=recipe.id,
                    ingredient_qty=request.form['ingredient_qty10'],
                    ingredient_measurement=request.form['ingredient_measurement10'],
                    ingredient_desc=request.form['ingredient_desc10']
                )
                db.session.add(ingredient10)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Ingredient10 did not add to database :(")

            # Write Ingredient 11
            try:
                ingredient11 = Ingredient(
                    # ingredient_qty=request.form('ingredient_qty')
                    recipe_id=recipe.id,
                    ingredient_qty=request.form['ingredient_qty11'],
                    ingredient_measurement=request.form['ingredient_measurement11'],
                    ingredient_desc=request.form['ingredient_desc11']
                )
                db.session.add(ingredient11)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Ingredient11 did not add to database :(")

            # Write Ingredient 12
            try:
                ingredient12 = Ingredient(
                    # ingredient_qty=request.form('ingredient_qty')
                    recipe_id=recipe.id,
                    ingredient_qty=request.form['ingredient_qty12'],
                    ingredient_measurement=request.form['ingredient_measurement12'],
                    ingredient_desc=request.form['ingredient_desc12']
                )
                db.session.add(ingredient12)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Ingredient12 did not add to database :(")

    return render_template('add.html', output=output)


# Define route for page to view all recipes
@app.route('/all_recipes', methods=['GET', 'POST'])
def all_recipes():
    recipe_list = Recipe.query.all()
    return render_template("all_recipes.html", recipe_list=recipe_list)


# Define route for page to view detailed info about one recipe
@app.route('/recipe/<recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id).first_or_404()
    return render_template('recipe_detail.html', recipe=recipe)


if __name__ == '__main__':
    app.run()
