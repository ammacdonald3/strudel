from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
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

from models import Recipe, Ingredient, Recipe_Step, App_User, LoginForm, RegistrationForm, Current_Meal, User_Recipe, Favorite_Recipe, Shopping_List

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
@login_required
def meal_selector():
    output = []
    if request.method == "POST":
        
        try:
            # Update user's current meal list to inactivate all meals
            db.session.query(Current_Meal).filter(Current_Meal.app_user_id==current_user.id).update(dict(active_ind=False))

            db.session.flush()
            db.session.commit()

            # Retrieve a list of all recipes uploaded by user
            # TO BE CHANGED in future to be a list of user's favorite meals
            # your_recipe_list = (db.session.query(Recipe).filter(Recipe.created_by==current_user.id)).order_by(Recipe.recipe_name).all()

            # Retrieve a list of user's favorite breakfast recipes
            favorite_bfast_recipe_list = (db.session.query(Recipe, Favorite_Recipe).join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id).filter(Favorite_Recipe.app_user_id==current_user.id).filter(Recipe.meal_breakfast==True)).order_by(Recipe.recipe_name).all()

            # Retrieve a list of user's favorite lunch recipes
            favorite_lunch_recipe_list = (db.session.query(Recipe, Favorite_Recipe).join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id).filter(Favorite_Recipe.app_user_id==current_user.id).filter(Recipe.meal_lunch==True)).order_by(Recipe.recipe_name).all()

            # Retrieve a list of user's favorite dinner recipes
            favorite_dinner_recipe_list = (db.session.query(Recipe, Favorite_Recipe).join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id).filter(Favorite_Recipe.app_user_id==current_user.id).filter(Recipe.meal_dinner==True)).order_by(Recipe.recipe_name).all()


            # Retrieve number of days of meals to generate per user input form
            num_bfast_meals = int(request.form['num_bfast_meals'])
            num_lunch_meals = int(request.form['num_lunch_meals'])
            num_dinner_meals = int(request.form['num_dinner_meals'])

            
            # If the total number of user's recipes is <= number of days' meals needed, just return entire list of user's recipes
            # Otherwise, randomly pick unique recipes based on number of days' meals needed

            # Breakfast
            if len(favorite_bfast_recipe_list) > num_bfast_meals:
                selected_bfast_meals_list = random.sample(favorite_bfast_recipe_list, num_bfast_meals)
            else:
                selected_bfast_meals_list = favorite_bfast_recipe_list

            # Lunch
            if len(favorite_lunch_recipe_list) > num_lunch_meals:
                selected_lunch_meals_list = random.sample(favorite_lunch_recipe_list, num_lunch_meals)
            else:
                selected_lunch_meals_list = favorite_lunch_recipe_list

            # Dinner
            if len(favorite_dinner_recipe_list) > num_dinner_meals:
                selected_dinner_meals_list = random.sample(favorite_dinner_recipe_list, num_dinner_meals)
            else:
                selected_dinner_meals_list = favorite_dinner_recipe_list


            # Insert selected breakfast meals to current_meal table
            day_counter = 0
            for val in selected_bfast_meals_list:
                day_counter += 1
                current_meal = Current_Meal(
                    recipe_id=val.Recipe.recipe_id,
                    app_user_id=current_user.id,
                    day_number=day_counter,
                    meal='breakfast',
                    active_ind=True,
                    insert_datetime=datetime.now()
                )
                db.session.add(current_meal)
                db.session.flush()
                db.session.commit()

            # Insert selected lunch meals to current_meal table
            day_counter = 0
            for val in selected_lunch_meals_list:
                day_counter += 1
                current_meal = Current_Meal(
                    recipe_id=val.Recipe.recipe_id,
                    app_user_id=current_user.id,
                    day_number=day_counter,
                    meal='lunch',
                    active_ind=True,
                    insert_datetime=datetime.now()
                )
                db.session.add(current_meal)
                db.session.flush()
                db.session.commit()

            # Insert selected dinner meals to current_meal table
            day_counter = 0
            for val in selected_dinner_meals_list:
                day_counter += 1
                current_meal = Current_Meal(
                    recipe_id=val.Recipe.recipe_id,
                    app_user_id=current_user.id,
                    day_number=day_counter,
                    meal='dinner',
                    active_ind=True,
                    insert_datetime=datetime.now()
                )
                db.session.add(current_meal)
                db.session.flush()
                db.session.commit()


            #print("selected_meals " + str(selected_meals_list), file=sys.stderr)

        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and your meals were not selected. Better luck in the future!")
            output.append(str(e))
            print(output)

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
    # Get list of user's selected breakfast meals
    selected_bfast_meals_list = (db.session.query(Recipe, Current_Meal).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).filter(Current_Meal.app_user_id==current_user.id).filter(Current_Meal.active_ind==True).filter(Current_Meal.meal=='breakfast').order_by(Current_Meal.day_number)).all()

    # Get list of user's selected lunch meals
    selected_lunch_meals_list = (db.session.query(Recipe, Current_Meal).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).filter(Current_Meal.app_user_id==current_user.id).filter(Current_Meal.active_ind==True).filter(Current_Meal.meal=='lunch').order_by(Current_Meal.day_number)).all()

    # Get list of user's selected dinner meals
    selected_dinner_meals_list = (db.session.query(Recipe, Current_Meal).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).filter(Current_Meal.app_user_id==current_user.id).filter(Current_Meal.active_ind==True).filter(Current_Meal.meal=='dinner').order_by(Current_Meal.day_number)).all()


    return render_template('meal_plan.html', selected_bfast_meals_list=selected_bfast_meals_list, selected_lunch_meals_list=selected_lunch_meals_list, selected_dinner_meals_list=selected_dinner_meals_list)

    

# Define route for shopping list page
@app.route('/shopping_list', methods=['GET', 'POST'])
@login_required
def shopping_list():
    output = []

    if request.method == "POST":

        # Path for manually adding new shopping list items
        if "add_submit" in request.form:
            try:
                shopping_list_item = request.form['add_item']

                # Retrieve the current items in the shopping list
                shop_list = (db.session.query(
                    Shopping_List
                ).filter(
                    Shopping_List.app_user_id==current_user.id
                ).order_by(Shopping_List.item_sort).all())


                # Delete existing shopping list
                Shopping_List.query.filter_by(app_user_id=current_user.id).delete()


                # Insert new item first
                shopping_list = Shopping_List(
                    item_desc=shopping_list_item,
                    recipe_id=None,
                    ingredient_id=None,
                    app_user_id=current_user.id,
                    item_sort=0,
                    checked_status=False,
                    insert_datetime=datetime.now()
                )
                
                db.session.add(shopping_list)
                db.session.flush()
                db.session.commit()

                # Reinsert remaining shopping list items second
                ingredient_counter = 1
                for item in shop_list:
                    shopping_list = Shopping_List(
                        item_desc=item.item_desc,
                        recipe_id=item.recipe_id,
                        ingredient_id=item.ingredient_id,
                        app_user_id=current_user.id,
                        item_sort=ingredient_counter,
                        checked_status=item.checked_status,
                        insert_datetime=item.insert_datetime
                    )
                    ingredient_counter += 1
                    db.session.add(shopping_list)
                    db.session.flush()
                    db.session.commit()

            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and your shopping list was not generated. Better luck in the future!")
                output.append(str(e))
                print(output)


        # Path for auto-generating shopping list from meal plan
        if "generate_submit" in request.form:
            try:

                # Delete existing shopping list
                # Shopping_List.query.filter_by(app_user_id=current_user.id).delete()


                # Retrieve list of current shopping list ingredient IDs
                current_shop_list = (db.session.query(
                    Shopping_List
                ).filter(
                    Shopping_List.app_user_id==current_user.id
                ))

                ingredient_ids_list = []
                for item in current_shop_list:
                    ingredient_ids_list.append(item.ingredient_id)


                # Retrieve a list of ingredients for current meals
                shop_list = (db.session.query(Ingredient, Current_Meal).join(Current_Meal, Ingredient.recipe_id==Current_Meal.recipe_id).filter(Current_Meal.app_user_id==current_user.id).filter(Current_Meal.active_ind==True)).all()


                # Insert ingredients from selected meals into shopping_list table
                # Only insert ingredients that do not yet exist in the table for the respective user
                ingredient_counter = 0
                for item in shop_list:
                    if item.Ingredient.ingredient_id not in ingredient_ids_list:
                        shopping_list = Shopping_List(
                            item_desc=item.Ingredient.ingredient_desc,
                            recipe_id=item.Current_Meal.recipe_id,
                            ingredient_id=item.Ingredient.ingredient_id,
                            app_user_id=current_user.id,
                            item_sort=ingredient_counter,
                            checked_status=False,
                            insert_datetime=datetime.now()
                        )
                        ingredient_counter += 1
                        db.session.add(shopping_list)
                        db.session.flush()
                        db.session.commit()


            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and your shopping list was not generated. Better luck in the future!")
                output.append(str(e))
                print(output)


        # Path for deleting custom-added items from shopping list:
        if "del_custom_submit" in request.form:
            try:

                # Delete existing shopping list
                Shopping_List.query.filter_by(app_user_id=current_user.id).filter_by(recipe_id=None).delete()

                db.session.flush()
                db.session.commit()


            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and your shopping list was not deleted. Better luck in the future!")
                output.append(str(e))
                print(output)


        # Path for deleting auto-generated items from shopping list:
        if "del_auto_submit" in request.form:
            try:

                # Delete existing shopping list
                Shopping_List.query.filter(Shopping_List.recipe_id.isnot(None)).filter_by(app_user_id=current_user.id).delete()

                db.session.flush()
                db.session.commit()

            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and your shopping list was not deleted. Better luck in the future!")
                output.append(str(e))
                print(output)


        # Path for deleting all items from shopping list:
        if "del_all_submit" in request.form:
            try:

                # Delete existing shopping list
                Shopping_List.query.filter_by(app_user_id=current_user.id).delete()

                db.session.flush()
                db.session.commit()


            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and your shopping list was not deleted. Better luck in the future!")
                output.append(str(e))
                print(output)
        

    shop_list = (db.session.query(
        Shopping_List, 
        Recipe
    ).outerjoin(
        Recipe, Recipe.recipe_id==Shopping_List.recipe_id
    ).filter(
        Shopping_List.app_user_id==current_user.id
    ).order_by(Shopping_List.item_sort).all())
    
    return render_template('shopping_list.html', shop_list=shop_list)


# Define route for checking off shopping list items
@app.route('/_shopping_list_items', methods=['GET', 'POST'])
@login_required
def _shopping_list_items():
    status = request.form.get('status')
    s_list_id = request.form.get('s_list_id')

    if status == 'checked':
        db.session.query(Shopping_List).filter(Shopping_List.shopping_list_id==s_list_id).update(dict(checked_status=True))
    elif status == 'unchecked':
        db.session.query(Shopping_List).filter(Shopping_List.shopping_list_id==s_list_id).update(dict(checked_status=False))
    
    db.session.flush()
    db.session.commit()

    shop_list = (db.session.query(
        Shopping_List, 
        Recipe
    ).join(
        Recipe, Recipe.recipe_id==Shopping_List.recipe_id
    ).filter(
        Shopping_List.app_user_id==current_user.id
    ).order_by(Shopping_List.item_sort).all())

    return render_template('shopping_list.html', shop_list=shop_list)


# Define route for deleting shopping list items
@app.route('/_del_shopping_list_items', methods=['GET', 'POST'])
@login_required
def _del_shopping_list_items():
    s_list_id = request.form.get('s_list_id')

    Shopping_List.query.filter_by(shopping_list_id=s_list_id).delete()

    db.session.flush()
    db.session.commit()

    shop_list = (db.session.query(
        Shopping_List, 
        Recipe
    ).join(
        Recipe, Recipe.recipe_id==Shopping_List.recipe_id
    ).filter(
        Shopping_List.app_user_id==current_user.id
    ).order_by(Shopping_List.item_sort).all())

    return render_template('shopping_list.html', shop_list=shop_list)


# Define route for resorting shopping list items
@app.route('/_shopping_list_sort', methods=['GET', 'POST'])
@login_required
def _shopping_list_sort():
    # status = request.form.get('status')
    # s_list_id = request.form.get('s_list_id')

    # if status == 'checked':
    #     db.session.query(Shopping_List).filter(Shopping_List.shopping_list_id==s_list_id).update(dict(checked_status=True))
    # elif status == 'unchecked':
    #     db.session.query(Shopping_List).filter(Shopping_List.shopping_list_id==s_list_id).update(dict(checked_status=False))
    
    # db.session.flush()
    # db.session.commit()
    print('ITEM INDEX')
    print(request.get_data())

    shop_list = (db.session.query(
        Shopping_List, 
        Ingredient, 
        Recipe, 
        Current_Meal
    ).join(
        Ingredient, Ingredient.ingredient_id==Shopping_List.ingredient_id
    ).join(
        Recipe, Recipe.recipe_id==Ingredient.recipe_id
    ).join(
        Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id
    ).filter(
        Current_Meal.app_user_id==current_user.id
    ).filter(
        Current_Meal.active_ind==True
    ).order_by(Shopping_List.item_sort).all())

    return render_template('shopping_list.html', shop_list=shop_list)


# Define route for page to manually add recipes
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_recipe():
    output = []
    # If user submits data on input form, write to DB
    if request.method == "POST":
        # if 'recipe_name' not in request.form:
        #     print('RECIPE NAME MISSING')
        # if 'recipe_desc' not in request.form:
        #     print('RECIPE DESC MISSING')
        # if 'recipe_prep_time' not in request.form:
        #     print('RECIPE PREP TIME MISSING')
        # if 'recipe_cook_time' not in request.form:
        #     print('RECIPE COOK TIME MISSING')
        # if 'recipe_url' not in request.form:
        #     print('RECIPE URL MISSING')
        # if 'serving_size' not in request.form:
        #     print('RECIPE SERVING SIZE MISSING')
        # if 'diet_vegan' not in request.form:
        #     print('DIET VEGAN MISSING')
        # if 'diet_vegetarian' not in request.form:
        #     print('DIET VEGETARIAN MISSING')
        # if 'diet_gluten' not in request.form:
        #     print('DIET GLUTEN MISSING')
        # if 'meal_breakfast' not in request.form:
        #     print('BREAKFAST MISSING')
        # if 'meal_lunch' not in request.form:
        #     print('LUNCH MISSING')
        # if 'meal_dinner' not in request.form:
        #     print('DINNER MISSING')


        # Write recipe info
        try:
            # Parse recipe URLs
            url_input = request.form['recipe_url']
            manual_input_clean_url = clean(url_input)

            # Calculate recipe "total time" as this is not a user-input field. This field is necessary for auto-import library.
            prep_time = int(request.form['recipe_prep_time'])
            cook_time = int(request.form['recipe_cook_time'])
            total_time = prep_time + cook_time


            # HTML form only passes checked inputs
            # Below code calculates boolean value if the input exists
            if 'diet_vegan' in request.form:
                diet_vegan_input = bool(request.form['diet_vegan'])
            else:
                diet_vegan_input = False

            if 'diet_vegetarian' in request.form:
                diet_vegetarian_input = bool(request.form['diet_vegetarian'])
            else:
                diet_vegetarian_input = False

            if 'diet_gluten' in request.form:
                diet_gluten_input = bool(request.form['diet_gluten'])
            else:
                diet_gluten_input = False

            if 'meal_breakfast' in request.form:
                meal_breakfast_input = bool(request.form['meal_breakfast'])
            else:
                meal_breakfast_input = False

            if 'meal_lunch' in request.form:
                meal_lunch_input = bool(request.form['meal_lunch'])
            else:
                meal_lunch_input = False

            if 'meal_dinner' in request.form:
                meal_dinner_input = bool(request.form['meal_dinner'])
            else:
                meal_dinner_input = False

            
            # Insert data to RECIPE table
            recipe = Recipe(
                recipe_name=request.form['recipe_name'],
                recipe_desc=request.form['recipe_desc'],
                recipe_prep_time=prep_time,
                recipe_cook_time=cook_time,
                recipe_total_time=total_time,
                serving_size=request.form['serving_size'],
                recipe_url=manual_input_clean_url,
                diet_vegan=diet_vegan_input,
                diet_vegetarian=diet_vegetarian_input,
                diet_gluten=diet_gluten_input,
                meal_breakfast=meal_breakfast_input,
                meal_lunch=meal_lunch_input,
                meal_dinner=meal_dinner_input,
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
            print(output)
            

        # Insert data to INGREDIENT table
        for x in range(1, 50):
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
                print(output)

        # Insert data to RECIPE_STEP table
        counter = 1
        for x in range(1, 50):
            try:
                recipe_step = Recipe_Step(
                    recipe_id=recipe.recipe_id,
                    step_order=counter,
                    step_desc=request.form['recipe_step' + str(x)],
                    insert_datetime=datetime.now()
                )
                counter += 1
                db.session.add(recipe_step)
                db.session.commit()
            # Return error if database write was unsuccessful
            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and the instructions didn't write to the database. Better luck in the future!")
                output.append(str(e))
                print(output)

        # Insert data to USER_RECIPE table
        try:
            user_recipe = User_Recipe(
                recipe_id=recipe.recipe_id,
                app_user_id=current_user.id,
                user_rating=0,
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
            print(output)

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

    #len_i = len(ingredient_list)

    # If user submits data on input form, write to DB
    if request.method == "POST" and recipe.created_by == current_user.id:
        # Write recipe info
        try:
            output = []
            # Parse recipe URLs
            url_input = request.form['recipe_url']
            manual_input_clean_url = clean(url_input)

            # Calculate recipe "total time" as this is not a user-input field. This field is necessary for auto-import library.
            prep_time = int(request.form['recipe_prep_time'])
            cook_time = int(request.form['recipe_cook_time'])
            total_time = prep_time + cook_time
            
            # Insert data to RECIPE table
            # recipe = Recipe(
            #     recipe_name=request.form['recipe_name'],
            #     recipe_desc=request.form['recipe_desc'],
            #     recipe_prep_time=prep_time,
            #     recipe_cook_time=cook_time,
            #     recipe_total_time=total_time,
            #     serving_size=request.form['serving_size'],
            #     recipe_url=manual_input_clean_url,
            #     diet_vegan=convert_bool(request.form.get('diet_vegan')),
            #     diet_vegetarian=convert_bool(request.form.get('diet_vegetarian')),
            #     diet_gluten=convert_bool(request.form.get('diet_gluten')),
            #     meal_breakfast=convert_bool(request.form.get('meal_breakfast')),
            #     meal_lunch=convert_bool(request.form.get('meal_lunch')),
            #     meal_dinner=convert_bool(request.form.get('meal_dinner')),
            #     created_by=current_user.id,
            #     insert_datetime=datetime.now()
            # )
            # print("PRINT PRINT PRINT")
            # print(request.form['recipe_name']),
            # print(request.form['recipe_desc']),
            # print(prep_time),
            # print(cook_time),
            # print(total_time),
            # print(request.form['serving_size']),
            # print(manual_input_clean_url),
            # print(bool(request.form['diet_vegan']),),
            # print(bool(request.form['diet_vegetarian'])),
            # print(bool(request.form['diet_gluten'])),
            # print(bool(request.form['meal_breakfast'])),
            # print(bool(request.form['meal_lunch'])),
            # print(bool(request.form['meal_dinner'])),
            # print(current_user.id),
            # print(datetime.now())


            # HTML form only passes checked inputs
            # Below code calculates boolean value if the input exists
            if 'diet_vegan' in request.form:
                diet_vegan_input = bool(request.form['diet_vegan'])
            else:
                diet_vegan_input = False

            if 'diet_vegetarian' in request.form:
                diet_vegetarian_input = bool(request.form['diet_vegetarian'])
            else:
                diet_vegetarian_input = False

            if 'diet_gluten' in request.form:
                diet_gluten_input = bool(request.form['diet_gluten'])
            else:
                diet_gluten_input = False

            if 'meal_breakfast' in request.form:
                meal_breakfast_input = bool(request.form['meal_breakfast'])
            else:
                meal_breakfast_input = False

            if 'meal_lunch' in request.form:
                meal_lunch_input = bool(request.form['meal_lunch'])
            else:
                meal_lunch_input = False

            if 'meal_dinner' in request.form:
                meal_dinner_input = bool(request.form['meal_dinner'])
            else:
                meal_dinner_input = False

            recipe.recipe_name=request.form['recipe_name']
            recipe.recipe_desc=request.form['recipe_desc']
            recipe.recipe_prep_time=prep_time
            recipe.recipe_cook_time=cook_time
            recipe.recipe_total_time=total_time
            recipe.serving_size=request.form['serving_size']
            recipe.recipe_url=manual_input_clean_url
            recipe.diet_vegan=diet_vegan_input
            recipe.diet_vegetarian=diet_vegetarian_input
            recipe.diet_gluten=diet_gluten_input
            recipe.meal_breakfast=meal_breakfast_input
            recipe.meal_lunch=meal_lunch_input
            recipe.meal_dinner=meal_dinner_input
            recipe.created_by=current_user.id
            recipe.insert_datetime=datetime.now()

            #db.session.add(recipe)
            db.session.merge(recipe)
            db.session.flush()
            db.session.commit()
            #output.append("Recipe successfully added!")

        # Return error if database write was unsuccessful
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
            print(str(e))

        # Delete existing ingredients
        Ingredient.query.filter_by(recipe_id=recipe_id).delete()
        db.session.flush()
        db.session.commit()

        # Insert data to INGREDIENT table
        for x in range(1, 50):
            try:
                # Insert new ingredients
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
                output.append("Application encountered an error, and the Ingredient info didn't write to the database. Better luck in the future!")
                output.append("Ingredient " + str(x) + " did not add to database!!")
                output.append(str(e))
                print(output)


        # Delete exising recipe steps
        Recipe_Step.query.filter_by(recipe_id=recipe_id).delete()
        db.session.flush()
        db.session.commit()

        # Insert data to RECIPE_STEP table
        counter = 1
        for x in range(1, 50):
            try:
                # Insert new recipe steps
                recipe_step = Recipe_Step(
                    recipe_id=recipe.recipe_id,
                    step_order=counter,
                    step_desc=request.form['recipe_step' + str(x)],
                    insert_datetime=datetime.now()
                )
                counter += 1
                db.session.add(recipe_step)
                db.session.commit()
            # Return error if database write was unsuccessful
            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and the Recipe Step info didn't write to the database. Better luck in the future!")
                output.append("Recipe Step " + str(x) + " did not add to database!!")
                output.append(str(e))
                print(output)


        # Insert data to USER_RECIPE table
        try:
            user_recipe = User_Recipe(
                recipe_id=recipe.recipe_id,
                app_user_id=current_user.id,
                user_rating=0,
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
                print(output)


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
        try:
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
                    diet_vegetarian=False,
                    diet_vegan=False,
                    diet_gluten=False,
                    meal_breakfast=False,
                    meal_lunch=False,
                    meal_dinner=False,
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
            
        except:
            error = 'This website is not supported at this time. Please manually add this recipe, and use the Auto Import function for one of the supported websites below.'
            return render_template("auto_import.html", error=error)

    # When not posting form, render the auto_import.html template (main page for this route)
    return render_template("auto_import.html", output=output)



# Define route for page to view all recipes
@app.route('/all_recipes', methods=['GET', 'POST'])
@login_required
def all_recipes():
    # Your favorite recipes (created both by you and others)
    favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe).join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id).filter(Favorite_Recipe.app_user_id==current_user.id)).order_by(Recipe.recipe_name).all()
    #print(favorite_recipe_list)
    # Recipes created by you
    your_recipe_list = (db.session.query(Recipe).filter(Recipe.created_by==current_user.id)).order_by(Recipe.recipe_name).all()

    # Recipes created by others
    other_recipe_list = (db.session.query(Recipe).filter(Recipe.created_by!=current_user.id)).order_by(Recipe.recipe_name).all()

    # Render the all_recipes.html template (main page for this route)
    return render_template("all_recipes.html", favorite_recipe_list=favorite_recipe_list, your_recipe_list=your_recipe_list, other_recipe_list=other_recipe_list)


# Define route for page to view detailed info about one recipe
@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
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
    favorite = db.session.query(Favorite_Recipe).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).first()
    ingredient_list = Ingredient.query.filter_by(recipe_id=recipe_id)
    step_list = Recipe_Step.query.filter_by(recipe_id=recipe_id)

    output = []
    # If user selects 'add to favorites' button, add the user/recipe combo to favorites table:
    if request.method == "POST" and favorite == None:
        # Scrape external website and clean data for write to the DB
        try:
            favorite_recipe = Favorite_Recipe(
                recipe_id=recipe_id,
                app_user_id=current_user.id,
                owner_ind=True,
                insert_datetime=datetime.now()
            )

            db.session.add(favorite_recipe)
            db.session.flush()
            db.session.commit()

            favorite = favorite_recipe

            return render_template('recipe_detail.html', recipe=recipe, ingredient_list=ingredient_list, step_list=step_list, favorite=favorite)

            
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
            print('ERROR ERROR ERROR')
            print(output)
        

    # If user select 'remove from favorites' button, delete the user/recipe combo from the favorites table:
    elif request.method == "POST":
        try:
            #db.session.query(Favorite_Recipe).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).delete()
            db.session.delete(favorite)
            db.session.flush()
            db.session.commit()

            favorite = None

            return render_template('recipe_detail.html', recipe=recipe, ingredient_list=ingredient_list, step_list=step_list, favorite=favorite)
        
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the favorite wasn't deleted from the database. Better luck in the future!")
            output.append(str(e))
            print('ERROR ERROR ERROR')
            print(output)

    # If user is the owner of the recipe, pass a flag to render the 'Edit' button
    if recipe.created_by == current_user.id:
        owner_ind = True
    else:
        owner_ind = False

    # Render the recipe_detail.html template (main page for this route)
    return render_template('recipe_detail.html', recipe=recipe, ingredient_list=ingredient_list, step_list=step_list, favorite=favorite, owner_ind=owner_ind)
    
    

# Define route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        app_user = App_User.query.filter_by(app_username=form.app_username.data).first()
        if app_user is None or not app_user.check_password(form.password.data):
            # flash('Invalid username or password')
            error = 'Invalid username or password'
            # return redirect(url_for('login'))
            return render_template('login.html', title='Sign In', form=form, error=error)
        login_user(app_user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    if form.validate_on_submit():
        app_user = App_User.query.filter_by(app_username=form.app_username.data).first()
        if app_user is None or not app_user.check_password(form.password.data):
            # flash('Invalid username or password')
            error = 'Invalid username or password'
            # return redirect(url_for('login'))
            return render_template('login.html', title='Sign In', form=form, error=error)
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