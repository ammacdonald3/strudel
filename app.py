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

from models import Recipe, Ingredient, Recipe_Step, App_User, LoginForm, RegistrationForm, Current_Meal, User_Recipe, Favorite_Recipe

# Function to clean URL input
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


# Function to convert form input true/false to python boolean
def convert_bool(form_input):
    if form_input == 'True':
        return True
    else:
        return False


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
            # Update user's current meal list to inactivate all meals
            db.session.query(Current_Meal).filter(Current_Meal.app_user_id==current_user.id).update(dict(active_ind=False))

            # Retrieve a list of all recipes uploaded by user
            # TO BE CHANGED in future to be a list of user's favorite meals
            your_recipe_list = (db.session.query(Recipe).filter(Recipe.created_by==current_user.id)).order_by(Recipe.recipe_name).all()

            # Retrieve number of days of meals to generate per user input form
            num_days = int(request.form['num_days'])
            
            # If the total number of user's recipes is <= number of days' meals needed, just return entire list of user's recipes
            # Otherwise, randomly pick unique recipes based on number of days' meals needed
            if len(your_recipe_list) > num_days:
                selected_meals_list = random.sample(your_recipe_list, num_days)
            else:
                selected_meals_list = your_recipe_list


            day_counter = 0
            for val in selected_meals_list:
                day_counter += 1
                current_meal = Current_Meal(
                    recipe_id=val.recipe_id,
                    app_user_id=current_user.id,
                    day_number=day_counter,
                    active_ind=True,
                    insert_datetime=datetime.now()
                )
                db.session.add(current_meal)
                db.session.flush()
                db.session.commit()

            print("selected_meals " + str(selected_meals_list), file=sys.stderr)

        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and your meals were not selected. Better luck in the future!")
            output.append(str(e))

        # Redirect to meal_plan.html page so that data pulls from database
        return redirect('meal_plan')

        # Comment out above line and uncomment below line to see application errors
        #return render_template('meal_plan.html', output=output)

    # When not posting form, render the meal_selector.html template (main page for this route)
    return render_template('meal_selector.html', output=output)


# Define route for meal plan page
@app.route('/meal_plan', methods=['GET', 'POST'])
@login_required
def meal_plan():
    selected_meals_list = (db.session.query(Recipe, Current_Meal).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).filter(Current_Meal.app_user_id==current_user.id).filter(Current_Meal.active_ind==True).order_by(Current_Meal.day_number)).all()
    return render_template('meal_plan.html', selected_meals_list=selected_meals_list)

    

# Define route for shopping list page
@app.route('/shopping_list')
@login_required
def shopping_list():
    shop_list = (db.session.query(Ingredient, Recipe, Current_Meal).join(Recipe, Recipe.recipe_id==Ingredient.recipe_id).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).filter(Current_Meal.app_user_id==current_user.id).filter(Current_Meal.active_ind==True)).all()
    return render_template('shopping_list.html', shop_list=shop_list)



# Define route for page to manually add recipes
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_recipe():
    output = []
    # If user submits data on input form, write to DB
    if request.method == "POST":
        # Write recipe info
        try:
            # Parse recipe URLs
            url_input = request.form['recipe_url']
            manual_input_clean_url = clean(url_input)

            # Calculate recipe "total time" as this is not a user-input field. This field is necessary for auto-import library.
            prep_time = request.form['recipe_prep_time']
            cook_time = request.form['recipe_cook_time']
            total_time = prep_time + cook_time
            
            # Insert data to RECIPE table
            recipe = Recipe(
                recipe_name=request.form['recipe_name'],
                recipe_desc=request.form['recipe_desc'],
                recipe_prep_time=prep_time,
                recipe_cook_time=cook_time,
                recipe_total_time=total_time,
                serving_size=request.form['serving_size'],
                recipe_url=manual_input_clean_url,
                diet_vegan=convert_bool(request.form.get('diet_vegan')),
                diet_vegetarian=convert_bool(request.form.get('diet_vegetarian')),
                diet_gluten=convert_bool(request.form.get('diet_gluten')),
                meal_time=request.form.get('meal_time'),
                created_by=current_user.id,
                insert_datetime=datetime.now()
            )
            db.session.add(recipe)
            db.session.flush()
            db.session.commit()
            #output.append("Recipe successfully added!")
        # Return error if database write was unsuccessful
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
            

        # Insert data to INGREDIENT table
        for x in range(1, 12):
            try:
                ingredient = Ingredient(
                    recipe_id=recipe.recipe_id,
                    ingredient_desc=request.form['ingredient_desc' + str(x)],
                    insert_datetime=datetime.now()
                )
                db.session.add(ingredient)
                db.session.commit()
            # Return error if database write was unsuccessful
            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and the ingredients didn't write to the database. Better luck in the future!")
                output.append(str(e))

        # Insert data to RECIPE_STEP table
        for x in range(1, 12):
            try:
                recipe_step = Recipe_Step(
                    recipe_id=recipe.recipe_id,
                    step_desc=request.form['recipe_step' + str(x)],
                    insert_datetime=datetime.now()
                )
                db.session.add(recipe_step)
                db.session.commit()
            # Return error if database write was unsuccessful
            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and the instructions didn't write to the database. Better luck in the future!")
                output.append(str(e))

        # Insert data to USER_RECIPE table
        try:
            user_recipe = User_Recipe(
                recipe_id=recipe.recipe_id,
                app_user_id=current_user.id,
                user_rating=5,
                owner_ind=True,
                insert_datetime=datetime.now()
            )
            db.session.add(user_recipe)
            db.session.flush()
            db.session.commit()
            #output.append("User_Recipe successfully added!")

        # Return error if database write was unsuccessful
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the user/recipe info didn't write to the database. Better luck in the future!")
            output.append(str(e))

        # Render recipe_confirm.html template after recipe is written to DB    
        return(render_template('recipe_confirm.html', recipe_id=recipe.recipe_id, recipe_name=request.form['recipe_name']))

    # When not posting form, render the add.html template (main page for this route)
    #return render_template('add.html', output=output)
    return render_template('add.html')



# Define route for page to modify existing recipes
@app.route('/edit/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    #output = []

    recipe = db.session.query(Recipe).filter_by(recipe_id=recipe_id).join(App_User).first()

    ingredient_list = Ingredient.query.filter_by(recipe_id=recipe_id)
    step_list = Recipe_Step.query.filter_by(recipe_id=recipe_id)

    # If user submits data on input form, write to DB
    if request.method == "POST":
        # Write recipe info
        try:
            # Parse recipe URLs
            url_input = request.form['recipe_url']
            manual_input_clean_url = clean(url_input)

            # Calculate recipe "total time" as this is not a user-input field. This field is necessary for auto-import library.
            prep_time = request.form['recipe_prep_time']
            cook_time = request.form['recipe_cook_time']
            total_time = prep_time + cook_time
            
            # Insert data to RECIPE table
            recipe = Recipe(
                recipe_name=request.form['recipe_name'],
                recipe_desc=request.form['recipe_desc'],
                recipe_prep_time=prep_time,
                recipe_cook_time=cook_time,
                recipe_total_time=total_time,
                serving_size=request.form['serving_size'],
                recipe_url=manual_input_clean_url,
                diet_vegan=convert_bool(request.form.get('diet_vegan')),
                diet_vegetarian=convert_bool(request.form.get('diet_vegetarian')),
                diet_gluten=convert_bool(request.form.get('diet_gluten')),
                meal_time=request.form.get('meal_time'),
                created_by=current_user.id,
                insert_datetime=datetime.now()
            )
            db.session.add(recipe)
            db.session.flush()
            db.session.commit()
            #output.append("Recipe successfully added!")
            
        # Return error if database write was unsuccessful
        except:
            #output.append("Recipe did not add to database :(")
            pass

        # Insert data to INGREDIENT table
        for x in range(1, 12):
            try:
                ingredient = Ingredient(
                    recipe_id=recipe.recipe_id,
                    ingredient_desc=request.form['ingredient_desc' + str(x)],
                    insert_datetime=datetime.now()
                )
                db.session.add(ingredient)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                #output.append("Ingredient " + str(x) + " did not add to database!!")
                pass

        # Insert data to RECIPE_STEP table
        for x in range(1, 12):
            try:
                recipe_step = Recipe_Step(
                    recipe_id=recipe.recipe_id,
                    step_desc=request.form['recipe_step' + str(x)],
                    insert_datetime=datetime.now()
                )
                db.session.add(recipe_step)
                db.session.commit()
            # Return error if database write was unsuccessful
            except:
                #output.append("Recipe Step " + str(x) + " did not add to database!!")
                pass

        # Insert data to USER_RECIPE table
        try:
            user_recipe = User_Recipe(
                recipe_id=recipe.recipe_id,
                app_user_id=current_user.id,
                user_rating=5,
                owner_ind=True,
                insert_datetime=datetime.now()
            )
            db.session.add(user_recipe)
            db.session.flush()
            db.session.commit()
            #output.append("User_Recipe successfully added!")
        # Return error if database write was unsuccessful
        except:
            #output.append("User_Recipe did not add to database :(")
            pass

        # Render recipe_confirm.html template after recipe is written to DB    
        return(render_template('recipe_confirm.html', recipe_id=recipe.recipe_id, recipe_name=request.form['recipe_name']))

    # When not posting form, render the add.html template (main page for this route)
    #return render_template('add.html', output=output)
    return render_template('edit_recipe.html', recipe=recipe, ingredient_list=ingredient_list, step_list=step_list)




# Define route to auto import / scrape recipe from external website
@app.route('/auto_import', methods=['GET', 'POST'])
@login_required
def auto_import():
    output = []
    # If user inputs URL, scrape website for recipe data and write to DB:
    if request.method == "POST":
        # Scrape external website and clean data for write to the DB
        try:
            url_input = request.form['recipe_url']
            auto_import_clean_url = clean(url_input)
            scraper = scrape_me(url_input)
            yields = scraper.yields()
            clean_yields = re.sub('[^0-9]','', yields)
        except:
            output.append("Recipe didn't scrape")

        # Insert data to RECIPE table
        try:
            recipe = Recipe(
                recipe_name=scraper.title(),
                recipe_desc='Imported from external website',
                recipe_prep_time=0,
                recipe_cook_time=scraper.total_time(),
                recipe_total_time=scraper.total_time(),
                serving_size=clean_yields,
                recipe_url=auto_import_clean_url,
                diet_vegetarian=None,
                diet_vegan=None,
                diet_gluten=None,
                meal_time='both',
                created_by=current_user.id,
                insert_datetime=datetime.now()
            )

            db.session.add(recipe)
            db.session.flush()
            db.session.commit()

            
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))


        # Insert data to INGREDENT table
        for item in scraper.ingredients():
            try:
                ingredient = Ingredient(
                    recipe_id=recipe.recipe_id,
                    ingredient_desc=item,
                    insert_datetime=datetime.now()
                )
                db.session.add(ingredient)
                db.session.flush()
                db.session.commit()

            # Return error if database write was unsuccessful
            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and the ingredients didn't write to the database. Better luck in the future!")
                output.append(str(e))

        # Insert data to RECIPE_STEP table
        instructions = scraper.instructions().split('\n')
        for step in instructions:
            try:
                recipe_step = Recipe_Step(
                    recipe_id=recipe.recipe_id,
                    step_desc=step,
                    insert_datetime=datetime.now()
                )
                db.session.add(recipe_step)
                db.session.flush()
                db.session.commit()
            # Return error if database write was unsuccessful
            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and the instructions didn't write to the database. Better luck in the future!")
                output.append(str(e))


        # Insert data to USER_RECIPE table
        """ try:
            user_recipe = User_Recipe(
                recipe_id=recipe.recipe_id,
                app_user_id=current_user.id,
                user_rating=5,
                owner_ind=True,
                insert_datetime=datetime.now()
            )
            db.session.add(user_recipe)
            db.session.flush()
            db.session.commit() """
            #output.append("User_Recipe successfully added!")

            # Render recipe_confirm.html template after recipe is written to DB
        return(render_template('recipe_confirm.html', recipe_id=recipe.recipe_id, recipe_name=scraper.title(), output=output))

        # Return error if database write was unsuccessful
        """ except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the user recipe didn't write to the database. Better luck in the future!")
            output.append(str(e)) """
        
    # When not posting form, render the auto_import.html template (main page for this route)
    return render_template("auto_import.html", output=output)



# Define route for page to view all recipes
@app.route('/all_recipes', methods=['GET', 'POST'])
@login_required
def all_recipes():
    # Your favorite recipes (created both by you and others)
    favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe).join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id).filter(Favorite_Recipe.app_user_id==current_user.id)).order_by(Recipe.recipe_name).all()
    
    # Recipes created by you
    your_recipe_list = (db.session.query(Recipe).filter(Recipe.created_by==current_user.id)).order_by(Recipe.recipe_name).all()

    # Recipes created by others
    other_recipe_list = (db.session.query(Recipe).filter(Recipe.created_by!=current_user.id)).order_by(Recipe.recipe_name).all()

    # Render the all_recipes.html template (main page for this route)
    return render_template("all_recipes.html", favorite_recipe_list=favorite_recipe_list, your_recipe_list=your_recipe_list, other_recipe_list=other_recipe_list)


# Define route for page to view detailed info about one recipe
@app.route('/recipe/<recipe_id>')
@login_required
def recipe_detail(recipe_id):
    #recipe = Recipe.query.filter_by(recipe_id=recipe_id)
    #recipe = (db.session.query(Recipe).filter(Recipe.recipe_id==recipe_id)).order_by(Recipe.recipe_name).all()
    #Recipe.query.filter_by(recipe_id=recipe_id).first_or_404()
    # BELOW COMMENT is an attempt to display "uploaded by username" on Recipe Detail page - DOES NOT WORK
    #recipe = (db.session.query(Recipe, App_User).join(App_User, Recipe.created_by==App_User.id).filter_by(id=recipe_id)).all()
    recipe = db.session.query(Recipe).filter_by(recipe_id=recipe_id).join(App_User).first()
    #recipe = db.session.query(Recipe).filter_by(recipe_id=recipe_id)
    #recipe = Recipe.query.filter_by(recipe_id=recipe_id)

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
        app_user = App_User.query.filter_by(app_username=form.app_username.data).first()
        if app_user is None or not app_user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(app_user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    if form.validate_on_submit():
        app_user = App_User.query.filter_by(app_username=form.app_username.data).first()
        if app_user is None or not app_user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(app_user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


# Define route for logout functionality
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Define route for registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        app_user = App_User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            app_username=form.app_username.data,
            app_email=form.app_email.data,
            insert_datetime=datetime.now()
            )
        app_user.set_password(form.password.data)
        db.session.add(app_user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



if __name__ == '__main__':
    app.run()