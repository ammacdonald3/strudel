from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URL'] = ['DATABASE_URL']
login = LoginManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)

from models import Recipe, Ingredient, Recipe_Step, User, LoginForm, RegistrationForm


# Define route for landing page
@app.route('/')
def index():
    return render_template('index.html')


# Define route for page to add recipes
@app.route('/add', methods=['GET', 'POST'])
@login_required
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

        # Write to user_recipe
        try:
            user_recipe = User_Recipe(
                recipe_id=recipe.id,
                user_id=2,
                owner_ind='Y'
            )
            db.session.add(user_recipe)
            db.session.commit()
        except:
            output.append("User ownership of this recipe was not established")

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
    
# Define route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



if __name__ == '__main__':
    app.run()
