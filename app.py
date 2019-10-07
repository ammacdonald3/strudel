from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import random
import sys
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URL'] = ['DATABASE_URL']
login = LoginManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)

from models import Recipe, Ingredient, Recipe_Step, User, LoginForm, RegistrationForm, Current_Meal, User_Recipe


# Define route for landing page
@app.route('/')
def index():
    return render_template('index.html')

# Define route for meal selector page
@app.route('/meal_selector', methods=['GET', 'POST'])
def meal_selector():
    output = []
    selected_meals_list = []
    if request.method == "POST":
        try:
            your_recipe_list = (db.session.query(Recipe, User_Recipe).join(User_Recipe, Recipe.id==User_Recipe.recipe_id).filter(User_Recipe.owner_ind==True).filter(User_Recipe.user_id==current_user.id)).order_by(Recipe.recipe_desc).all()

            selected_meals_list = random.sample(your_recipe_list, 4)

            print("selected_meals " + str(selected_meals_list), file=sys.stderr)

        except:
            output.append("Meals not selected")

        return render_template('meal_plan.html', output=output, selected_meals_list=selected_meals_list)

    return render_template('meal_selector.html', output=output, selected_meals_list=selected_meals_list)


# Define route for meal plan page
@app.route('/meal_plan', methods=['GET', 'POST'])
@login_required
def meal_plan():
    meal_plan_list = (db.session.query(Recipe, Current_Meal).join(Current_Meal, Recipe.id==Current_Meal.recipe_id).filter(Current_Meal.active_ind=='Y')).all()
    return render_template('meal_plan.html', meal_plan_list=meal_plan_list)

    

# Define route for shopping list page
@app.route('/shopping_list')
def shopping_list():
    shop_list = (db.session.query(Ingredient, Recipe, Current_Meal).join(Recipe, Recipe.id==Ingredient.recipe_id).join(Current_Meal, Recipe.id==Current_Meal.recipe_id).filter(Current_Meal.active_ind=='Y')).all()
    return render_template('shopping_list.html', shop_list=shop_list)


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
                recipe_cook_time=request.form['recipe_cook_time'],
                serving_size=request.form['serving_size'],
                diet_vegetarian=request.form.get('diet_vegetarian'),
                diet_vegan=request.form.get('diet_vegan'),
                diet_gluten=request.form.get('diet_gluten'),
                meal_time=request.form.get('meal_time')
            )
            db.session.add(recipe)
            db.session.flush()
            db.session.commit()
            output.append("Recipe successfully added!")
        # Return error if database write was unsuccessful
        except:
            output.append("Recipe did not add to database :(")

        for x in range(1, 12):
            try:
                ingredient = Ingredient(
                    recipe_id=recipe.id,
                    ingredient_qty=request.form['ingredient_qty' + str(x)],
                    ingredient_measurement=request.form['ingredient_measurement' + str(x)],
                    ingredient_desc=request.form['ingredient_desc' + str(x)]
                )
                db.session.add(ingredient)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Ingredient " + str(x) + " did not add to database!!")

        for x in range(1, 12):
            try:
                recipe_step = Recipe_Step(
                    recipe_id=recipe.id,
                    step_desc=request.form['recipe_step' + str(x)]
                )
                db.session.add(recipe_step)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                output.append("Recipe Step " + str(x) + " did not add to database!!")

        # Write user_recipe info
        try:
            user_recipe = User_Recipe(
                recipe_id=recipe.id,
                user_id=current_user.id,
                user_rating=5,
                owner_ind=True
            )
            db.session.add(user_recipe)
            db.session.flush()
            db.session.commit()
            output.append("User_Recipe successfully added!")
        # Return error if database write was unsuccessful
        except:
            output.append("User_Recipe did not add to database :(")

        return(render_template('recipe_confirm.html', recipe_id=recipe.id, recipe_name=request.form['recipe_name']))

    return render_template('add.html', output=output)


# Define route for page to view all recipes
@app.route('/all_recipes', methods=['GET', 'POST'])
@login_required
def all_recipes():
    your_recipe_list = (db.session.query(Recipe, User_Recipe).join(User_Recipe, Recipe.id==User_Recipe.recipe_id).filter(User_Recipe.owner_ind==True).filter(User_Recipe.user_id==current_user.id)).order_by(Recipe.recipe_desc).all()

    other_recipe_list = (db.session.query(Recipe, User_Recipe).join(User_Recipe, Recipe.id==User_Recipe.recipe_id).filter(User_Recipe.owner_ind==False).filter(User_Recipe.user_id==current_user.id)).order_by(Recipe.recipe_desc).all()


    return render_template("all_recipes.html", your_recipe_list=your_recipe_list, other_recipe_list=other_recipe_list)


# Define route for page to view detailed info about one recipe
@app.route('/recipe/<recipe_id>')
@login_required
def recipe_detail(recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id).first_or_404()
    ingredient_list = Ingredient.query.filter_by(recipe_id=recipe_id)
    step_list = Recipe_Step.query.filter_by(recipe_id=recipe_id)
    return render_template('recipe_detail.html', recipe=recipe, ingredient_list=ingredient_list, step_list=step_list)
    
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