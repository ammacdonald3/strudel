from flask import Flask, render_template, request, flash, redirect, url_for
#from Flask_SQLAlchemy import SQLAlchemy
import flask_sqlalchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from recipe_scrapers import scrape_me
from datetime import datetime
import re
import random
import sys
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URL'] = ['DATABASE_URL']
login = LoginManager(app)
login.login_view = 'login'
db = flask_sqlalchemy.SQLAlchemy(app)

from models import Recipe, Ingredient, Recipe_Step, User, LoginForm, RegistrationForm, Current_Meal, User_Recipe

# Clean URL input
def clean(url_input):
    if url_input[:12] == 'https://www.':
        clean_url = url_input[12:]
    elif url_input[:11] == 'http://www.':
        clean_url = url_input[11:]
    elif url_input[:8] == 'https://':
        clean_url = url_input[8:]
    elif url_input[:7] == 'http://':
        clean_url = url_input[7:]
    elif url_input[:4] == 'www.':
        clean_url = url_input[4:]
    else:
        clean_url = url_input
    return clean_url


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
            active_recipes = (db.session.query(Current_Meal).filter(Current_Meal.user_id==current_user.id).update(dict(active_ind=False)))
            your_recipe_list = (db.session.query(Recipe, User_Recipe).join(User_Recipe, Recipe.id==User_Recipe.recipe_id).filter(User_Recipe.owner_ind==True).filter(User_Recipe.user_id==current_user.id)).order_by(Recipe.recipe_desc).all()

            selected_meals_list = random.sample(your_recipe_list, 5)
            
            day_counter = 0
            for val in selected_meals_list:
                day_counter += 1
                current_meal = Current_Meal(
                    recipe_id=val.Recipe.id,
                    user_id=current_user.id,
                    day_number=day_counter,
                    active_ind=True
                )
                db.session.add(current_meal)
                db.session.flush()
                db.session.commit()

            print("selected_meals " + str(selected_meals_list), file=sys.stderr)

        except:
            output.append("Meals not selected")

        #return render_template('meal_plan.html', output=output, selected_meals_list=selected_meals_list)
        return redirect('meal_plan')

    #return render_template('meal_selector.html', output=output, selected_meals_list=selected_meals_list)
    return render_template('meal_selector.html', output=output)


# Define route for meal plan page
@app.route('/meal_plan', methods=['GET', 'POST'])
@login_required
def meal_plan():
    selected_meals_list = (db.session.query(Recipe, Current_Meal).join(Current_Meal, Recipe.id==Current_Meal.recipe_id).filter(Current_Meal.active_ind==True)).all()
    return render_template('meal_plan.html', selected_meals_list=selected_meals_list)

    

# Define route for shopping list page
@app.route('/shopping_list')
@login_required
def shopping_list():
    shop_list = (db.session.query(Ingredient, Recipe, Current_Meal).join(Recipe, Recipe.id==Ingredient.recipe_id).join(Current_Meal, Recipe.id==Current_Meal.recipe_id).filter(Current_Meal.active_ind==True)).all()
    return render_template('shopping_list.html', shop_list=shop_list)


# Define route for page to add recipes
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_recipe():
    #output = []
    # If user submits data on input form, write to DB
    if request.method == "POST":
        # Write recipe info
        try:
            # Parse recipe URLs
            url_input = request.form['recipe_url']
            manual_input_clean_url = clean(url_input)
            prep_time = request.form['recipe_prep_time']
            cook_time = request.form['recipe_cook_time']
            total_time = prep_time + cook_time
            
            recipe = Recipe(
                recipe_name=request.form['recipe_name'],
                recipe_desc=request.form['recipe_desc'],
                recipe_prep_time=prep_time,
                recipe_cook_time=cook_time,
                recipe_total_time=total_time,
                serving_size=request.form['serving_size'],
                recipe_url=manual_input_clean_url,
                diet_vegetarian=request.form.get('diet_vegetarian'),
                diet_vegan=request.form.get('diet_vegan'),
                diet_gluten=request.form.get('diet_gluten'),
                meal_time=request.form.get('meal_time'),
                insert_datetime=datetime.utcnow
            )
            db.session.add(recipe)
            db.session.flush()
            db.session.commit()
            #output.append("Recipe successfully added!")
        # Return error if database write was unsuccessful
        except:
            #output.append("Recipe did not add to database :(")
            pass

        for x in range(1, 12):
            try:
                ingredient = Ingredient(
                    recipe_id=recipe.id,
                    ingredient_desc=request.form['ingredient_desc' + str(x)]
                )
                db.session.add(ingredient)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                #output.append("Ingredient " + str(x) + " did not add to database!!")
                pass

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
                #output.append("Recipe Step " + str(x) + " did not add to database!!")
                pass

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
            #output.append("User_Recipe successfully added!")
        # Return error if database write was unsuccessful
        except:
            #output.append("User_Recipe did not add to database :(")
            pass

        return(render_template('recipe_confirm.html', recipe_id=recipe.id, recipe_name=request.form['recipe_name']))

    #return render_template('add.html', output=output)
    return render_template('add.html')

@app.route('/auto_import', methods=['GET', 'POST'])
@login_required
def auto_import():
    output = []
    # If user inputs URL, scrape website for recipe data and write to DB:
    if request.method == "POST":
        # Write recipe info
        try:
            url_input = request.form['recipe_url']
            auto_import_clean_url = clean(url_input)
            scraper = scrape_me(url_input)
            yields = scraper.yields()
            clean_yields = re.sub('[^0-9]','', yields)
        except:
            output.append("Recipe didn't scrape")


        try:
            recipe = Recipe(
                recipe_name=scraper.title(),
                recipe_desc='Imported from external website',
                recipe_prep_time=0,
                recipe_cook_time=0,
                recipe_total_time=scraper.total_time(),
                serving_size=clean_yields,
                recipe_url=auto_import_clean_url,
                diet_vegetarian=None,
                diet_vegan=None,
                diet_gluten=None,
                meal_time='both',
                insert_datetime=datetime.utcnow()
                #insert_datetime=None
            )

            db.session.add(recipe)
            db.session.flush()
            db.session.commit()

            
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))


        for item in scraper.ingredients():
            try:
                #quantity = float(re.sub('[^0-9]','', item))
                #desc = re.sub(r'\d+','', item)
                #quantity = item.partition(' ')[0]
                #desc = item.partition(' ')[2]
                ingredient = Ingredient(
                    recipe_id=recipe.id,
                    ingredient_desc=item
                )
                db.session.add(ingredient)
                db.session.flush()
                db.session.commit()
            # Return error if database write was unsuccessful
            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and the ingredients didn't write to the database. Better luck in the future!")
                output.append(str(e))


        instructions = scraper.instructions().split('\n')
        for step in instructions:
            try:
                recipe_step = Recipe_Step(
                    recipe_id=recipe.id,
                    step_desc=step
                )
                db.session.add(recipe_step)
                db.session.flush()
                db.session.commit()
            # Return error if database write was unsuccessful
            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and the instructions didn't write to the database. Better luck in the future!")
                output.append(str(e))


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
            #output.append("User_Recipe successfully added!")

            return(render_template('recipe_confirm.html', recipe_id=recipe.id, recipe_name=scraper.title()))

        # Return error if database write was unsuccessful
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the user recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
        

    return render_template("auto_import.html", output=output)

# Define route for page to view all recipes
@app.route('/all_recipes', methods=['GET', 'POST'])
@login_required
def all_recipes():
    your_recipe_list = (db.session.query(Recipe, User_Recipe).join(User_Recipe, Recipe.id==User_Recipe.recipe_id).filter(User_Recipe.owner_ind==True).filter(User_Recipe.user_id==current_user.id)).order_by(Recipe.recipe_name).all()
    #your_recipe_list = (db.session.query(Recipe, User_Recipe).join(User_Recipe, Recipe.id==User_Recipe.recipe_id).filter(User_Recipe.user_id==current_user.id)).order_by(Recipe.recipe_desc).all()

    other_recipe_list = (db.session.query(Recipe, User_Recipe).join(User_Recipe, Recipe.id==User_Recipe.recipe_id).filter(User_Recipe.owner_ind==False).filter(User_Recipe.user_id==current_user.id)).order_by(Recipe.recipe_name).all()
    #other_recipe_list = (db.session.query(Recipe, User_Recipe).join(User_Recipe, Recipe.id==User_Recipe.recipe_id).filter(User_Recipe.user_id==current_user.id)).order_by(Recipe.recipe_desc).all()


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