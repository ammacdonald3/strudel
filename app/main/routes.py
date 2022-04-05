from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort, send_from_directory, current_app
import flask_sqlalchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from recipe_scrapers import scrape_me
from datetime import datetime
from uuid import uuid4
from sqlalchemy import or_, func
import re
import random
import sys
import os
import imghdr
import json
import boto3
from google.oauth2 import id_token
from google.auth.transport import requests

#from app import app, db
from flask import current_app as app

from app import db

from app.models import Recipe, Ingredient, Recipe_Step, App_User, Current_Meal, User_Recipe, Favorite_Recipe, Shopping_List, App_Error

from app.main import bp


# Function to upload a file to an S3 bucket
def upload_file(file_name, bucket):
    #S3_BUCKET = os.environ.get('S3_BUCKET')
    object_name = file_name
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(
            file_name, bucket, object_name, ExtraArgs={'ACL': 'public-read'}
            )
        url = f'https://{BUCKET}.s3.amazonaws.com/{file_name}'
    except Exception as e:
            output = []
            output.append(str(e))
            print(output)
    return url


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


# Function for content validation on images
def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


# Define route for landing page
@bp.route('/')
def index():
    google_login_uri = current_app.config['GOOGLE_LOGIN_URI']
    google_client_id = current_app.config['GOOGLE_CLIENT_ID']
    return render_template('index.html', google_login_uri=google_login_uri, google_client_id=google_client_id)


# Define route for meal selector page
@bp.route('/meal_selector', methods=['GET', 'POST'])
@login_required
def meal_selector():
    output = []
    if request.method == "POST":
        
        try:
            # Update user's current meal list to inactivate all meals
            db.session.query(Current_Meal).filter(Current_Meal.app_user_id==current_user.id).update(dict(active_ind=False))

            db.session.flush()
            db.session.commit()

            # Retrieve number of days of meals to generate per user input form
            try:
                num_bfast_meals = int(request.form['num_bfast_meals'])
            except:
                num_bfast_meals = 0

            try:
                num_lunch_meals = int(request.form['num_lunch_meals'])
            except:
                num_lunch_meals = 0

            try:
                num_dinner_meals = int(request.form['num_dinner_meals'])
            except:
                num_dinner_meals = 0


            # If user wants to generate plan from Favorite recipes
            if request.form['recipe_source'] == 'fav':

                # Retrieve a list of user's favorite breakfast recipes
                bfast_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe \
                    .recipe_id).filter(Favorite_Recipe.app_user_id==current_user.id) \
                    .filter(Recipe.meal_breakfast==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's favorite lunch recipes
                lunch_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id) \
                    .filter(Favorite_Recipe.app_user_id==current_user.id) \
                    .filter(Recipe.meal_lunch==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's favorite dinner recipes
                dinner_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id) \
                    .filter(Favorite_Recipe.app_user_id==current_user.id) \
                    .filter(Recipe.meal_dinner==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

            
            # If user wants to generate plan from all recipes they uploaded
            elif request.form['recipe_source'] == 'you':

                # Retrieve a list of user's breakfast recipes
                bfast_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.created_by==current_user.id) \
                    .filter(Recipe.meal_breakfast==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's lunch recipes
                lunch_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.created_by==current_user.id) \
                    .filter(Recipe.meal_lunch==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's dinner recipes
                dinner_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.created_by==current_user.id) \
                    .filter(Recipe.meal_dinner==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()


            # If user wants to generate plan from the editor's picks
            elif request.form['recipe_source'] == 'editor':

                # Retrieve a list of editor's breakfast recipes
                bfast_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==1)) \
                    .filter(Recipe.meal_breakfast==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of editor's lunch recipes
                lunch_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==1)) \
                    .filter(Recipe.meal_lunch==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of editor's dinner recipes
                dinner_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==1)) \
                    .filter(Recipe.meal_dinner==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()


            # If user wants to generate plan from all recipes in the app
            elif request.form['recipe_source'] == 'all':

                # Retrieve a list of user's breakfast recipes
                bfast_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.meal_breakfast==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's lunch recipes
                lunch_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.meal_lunch==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's dinner recipes
                dinner_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.meal_dinner==True) \
                    .filter(Recipe.recipe_deleted==None)) \
                    .order_by(Recipe.recipe_name) \
                    .all()
            

            
            # If the total number of user's recipes is <= number of days' meals needed, just return entire list of user's recipes
            # Otherwise, randomly pick unique recipes based on number of days' meals needed

            # Breakfast
            if len(bfast_recipe_list) > num_bfast_meals:
                selected_bfast_meals_list = random.sample(bfast_recipe_list, num_bfast_meals)
            else:
                selected_bfast_meals_list = bfast_recipe_list

            # Lunch
            if len(lunch_recipe_list) > num_lunch_meals:
                selected_lunch_meals_list = random.sample(lunch_recipe_list, num_lunch_meals)
            else:
                selected_lunch_meals_list = lunch_recipe_list

            # Dinner
            if len(dinner_recipe_list) > num_dinner_meals:
                selected_dinner_meals_list = random.sample(dinner_recipe_list, num_dinner_meals)
            else:
                selected_dinner_meals_list = dinner_recipe_list

            
            # Below IF/ELSE is required because Favorite Recipes sqlalchemy object is referenced as val.Recipe.recipe_id, but User-Uploaded / All Recipes sqlalchemy objects are referenced as val.recipe_id
            if (request.form['recipe_source'] == 'fav') or (request.form['recipe_source'] == 'editor'):

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

            else:

                # Insert selected breakfast meals to current_meal table
                day_counter = 0
                for val in selected_bfast_meals_list:
                    day_counter += 1
                    current_meal = Current_Meal(
                        recipe_id=val.recipe_id,
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
                        recipe_id=val.recipe_id,
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
                        recipe_id=val.recipe_id,
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

            # Write errors to APP_ERROR table
            app_error = App_Error(
                    app_user_id=current_user.id,
                    insert_datetime=datetime.now(),
                    error_val=str(e)
                )
            db.session.add(app_error)
            db.session.flush()
            db.session.commit()


        # Redirect to meal_plan.html page so that data pulls from database
        return redirect('meal_plan')

        # Comment out above line and uncomment below line to see application errors
        #return render_template('meal_plan.html', output=output)

    # When not posting form, render the meal_selector.html template (main page for this route)
    return render_template('meal_selector.html', output=output)


# Define route for meal plan page
@bp.route('/meal_plan', methods=['GET', 'POST'])
@login_required
def meal_plan():

    # Get list of user's selected breakfast meals
    selected_bfast_meals_list = (db.session.query(Recipe, Current_Meal).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).filter(Current_Meal.app_user_id==current_user.id).filter(Current_Meal.active_ind==True).filter(Current_Meal.meal=='breakfast').order_by(Current_Meal.day_number)).all()

    bfast_length = len(selected_bfast_meals_list)

    if bfast_length != 0:
        bfast_exists = True
    else:
        bfast_exists = False 

    # Get list of user's selected lunch meals
    selected_lunch_meals_list = (db.session.query(Recipe, Current_Meal).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).filter(Current_Meal.app_user_id==current_user.id).filter(Current_Meal.active_ind==True).filter(Current_Meal.meal=='lunch').order_by(Current_Meal.day_number)).all()

    lunch_length = len(selected_lunch_meals_list)

    if lunch_length != 0:
        lunch_exists = True
    else:
        lunch_exists = False 


    # Get list of user's selected dinner meals
    selected_dinner_meals_list = (db.session.query(Recipe, Current_Meal).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).filter(Current_Meal.app_user_id==current_user.id).filter(Current_Meal.active_ind==True).filter(Current_Meal.meal=='dinner').order_by(Current_Meal.day_number)).all()

    dinner_length = len(selected_dinner_meals_list)

    if dinner_length != 0:
        dinner_exists = True
    else:
        dinner_exists = False 



    return render_template('meal_plan.html', selected_bfast_meals_list=selected_bfast_meals_list, selected_lunch_meals_list=selected_lunch_meals_list, selected_dinner_meals_list=selected_dinner_meals_list,
    bfast_exists=bfast_exists,
    lunch_exists=lunch_exists,
    dinner_exists=dinner_exists,
    bfast_length=bfast_length,
    lunch_length=lunch_length,
    dinner_length=dinner_length
    )

    

# Define route for shopping list page
@bp.route('/shopping_list', methods=['GET', 'POST'])
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

                # Write errors to APP_ERROR table
                app_error = App_Error(
                    app_user_id=current_user.id,
                    insert_datetime=datetime.now(),
                    error_val=str(e)
                )
                db.session.add(app_error)
                db.session.flush()
                db.session.commit()


        # Path for deleting auto-generated items from shopping list:
        # This code block is placed here intentionally to allow user to delete auto-generated items in the same workflow as generating new items
        if ("del_auto_submit" in request.form) or ("gen_with_delete_submit" in request.form):
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

                # Write errors to APP_ERROR table
                app_error = App_Error(
                    app_user_id=current_user.id,
                    insert_datetime=datetime.now(),
                    error_val=str(e)
                )
                db.session.add(app_error)
                db.session.flush()
                db.session.commit()


        # Path for auto-generating shopping list from meal plan
        if ("gen_without_delete_submit" in request.form) or ("gen_with_delete_submit" in request.form):
            try:

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

                # Write errors to APP_ERROR table
                app_error = App_Error(
                    app_user_id=current_user.id,
                    insert_datetime=datetime.now(),
                    error_val=str(e)
                )
                db.session.add(app_error)
                db.session.flush()
                db.session.commit()


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

                # Write errors to APP_ERROR table
                app_error = App_Error(
                    app_user_id=current_user.id,
                    insert_datetime=datetime.now(),
                    error_val=str(e)
                )
                db.session.add(app_error)
                db.session.flush()
                db.session.commit()


        


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

                # Write errors to APP_ERROR table
                app_error = App_Error(
                    app_user_id=current_user.id,
                    insert_datetime=datetime.now(),
                    error_val=str(e)
                )
                db.session.add(app_error)
                db.session.flush()
                db.session.commit()
        

    # Query for shopping list items
    shop_list = (db.session.query(
        Shopping_List, 
        Recipe
    ).outerjoin(
        Recipe, Recipe.recipe_id==Shopping_List.recipe_id
    ).filter(
        Shopping_List.app_user_id==current_user.id
    ).order_by(Shopping_List.checked_status).order_by(Shopping_List.insert_datetime.desc()).all())
    
    return render_template('shopping_list.html', shop_list=shop_list)


# Define route for checking off shopping list items with ajax
@bp.route('/_shopping_list_items', methods=['GET', 'POST'])
@login_required
def _shopping_list_items():
    status = request.form.get('status')
    s_list_id = request.form.get('s_list_id')

    # If user checked an item, update DB to flag it as checked
    if status == 'checked':
        db.session.query(Shopping_List).filter(Shopping_List.shopping_list_id==s_list_id).update(dict(checked_status=True))
    
    # If user unchecked an item, update DB to flag it as unchecked
    elif status == 'unchecked':
        db.session.query(Shopping_List).filter(Shopping_List.shopping_list_id==s_list_id).update(dict(checked_status=False))
    
    db.session.flush()
    db.session.commit()

    # Query for shopping list items
    shop_list = (db.session.query(
        Shopping_List, 
        Recipe
    ).join(
        Recipe, Recipe.recipe_id==Shopping_List.recipe_id
    ).filter(
        Shopping_List.app_user_id==current_user.id
    ).order_by(Shopping_List.item_sort).all())

    return render_template('shopping_list.html', shop_list=shop_list)


# Define route for manually adding recipe to meal plan
@bp.route('/_meal_plan', methods=['GET', 'POST'])
@login_required
def _meal_plan():
    status = request.form.get('status')
    recipe_id = request.form.get('recipe_id')

    # If user selected to add recipe to meal plan, update table
    if status == 'checked':
        # If recipe is categorized as a breakfast recipe, add to Meal Plan as a breakfast meal
        if (db.session.query(Recipe.meal_breakfast).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

            breakfast_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='breakfast').first()

            if breakfast_exists is None:

                current_meal = Current_Meal(
                    recipe_id=recipe_id,
                    app_user_id=current_user.id,
                    day_number=0,
                    meal='breakfast',
                    active_ind=True,
                    insert_datetime=datetime.now()
                )
                db.session.add(current_meal)
                db.session.flush()
                db.session.commit()

        # If recipe is categorized as a lunch recipe, add to Meal Plan as a lunch meal
        if (db.session.query(Recipe.meal_lunch).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

            lunch_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='lunch').first()

            if lunch_exists is None:

                current_meal = Current_Meal(
                    recipe_id=recipe_id,
                    app_user_id=current_user.id,
                    day_number=0,
                    meal='lunch',
                    active_ind=True,
                    insert_datetime=datetime.now()
                )
                db.session.add(current_meal)
                db.session.flush()
                db.session.commit()

        # If recipe is categorized as a dinner recipe, add to Meal Plan as a dinner meal
        if (db.session.query(Recipe.meal_dinner).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

            dinner_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='dinner').first()

            if dinner_exists is None:

                current_meal = Current_Meal(
                    recipe_id=recipe_id,
                    app_user_id=current_user.id,
                    day_number=0,
                    meal='dinner',
                    active_ind=True,
                    insert_datetime=datetime.now()
                )
                db.session.add(current_meal)
                db.session.flush()
                db.session.commit()
    
    # If user selected to remove recipe to meal plan, update table
    elif status == 'unchecked':
        db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).update(dict(active_ind=False))

        db.session.flush()
        db.session.commit()

    return render_template('all_recipes.html')


# Define route for clearing all items from meal plan
@bp.route('/_clear_meal_plan', methods=['GET','POST'])
@login_required
def _clear_meal_plan():
    
    # Inactivate all items from user's meal plan
    try:
        db.session.query(Current_Meal).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).update(dict(active_ind=False))

        db.session.flush()
        db.session.commit()
    
    # Error handling
    except Exception as e:
            output=[]
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
            print(output)

            # Write errors to APP_ERROR table
            app_error = App_Error(
                app_user_id=current_user.id,
                insert_datetime=datetime.now(),
                error_val=str(e)
            )
            db.session.add(app_error)
            db.session.flush()
            db.session.commit()

    return render_template('meal_plan.html')


# Define route for manually adding BREAKFAST recipe to meal plan
@bp.route('/_meal_breakfast', methods=['GET', 'POST'])
@login_required
def _meal_breakfast():
    status = request.form.get('status')
    recipe_id = request.form.get('recipe_id')

    # If user selected to add recipe to meal plan, update table
    if status == 'checked':

        breakfast_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='breakfast').first()

        if breakfast_exists is None:

            current_meal = Current_Meal(
                recipe_id=recipe_id,
                app_user_id=current_user.id,
                day_number=0,
                meal='breakfast',
                active_ind=True,
                insert_datetime=datetime.now()
            )
            db.session.add(current_meal)
            db.session.flush()
            db.session.commit()

    
    # If user selected to remove recipe to meal plan, update table
    elif status == 'unchecked':
        db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).update(dict(active_ind=False))

        db.session.flush()
        db.session.commit()

    return render_template('all_recipes.html')


# Define route for manually adding LUNCH recipe to meal plan
@bp.route('/_meal_lunch', methods=['GET', 'POST'])
@login_required
def _meal_lunch():
    status = request.form.get('status')
    recipe_id = request.form.get('recipe_id')

    # If user selected to add recipe to meal plan, update table
    if status == 'checked':

        lunch_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='lunch').first()

        if lunch_exists is None:

            current_meal = Current_Meal(
                recipe_id=recipe_id,
                app_user_id=current_user.id,
                day_number=0,
                meal='lunch',
                active_ind=True,
                insert_datetime=datetime.now()
            )
            db.session.add(current_meal)
            db.session.flush()
            db.session.commit()

    
    # If user selected to remove recipe to meal plan, update table
    elif status == 'unchecked':
        db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).update(dict(active_ind=False))

        db.session.flush()
        db.session.commit()

    return render_template('all_recipes.html')


# Define route for manually adding DINNER recipe to meal plan
@bp.route('/_meal_dinner', methods=['GET', 'POST'])
@login_required
def _meal_dinner():
    status = request.form.get('status')
    recipe_id = request.form.get('recipe_id')

    # If user selected to add recipe to meal plan, update table
    if status == 'checked':

        dinner_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='dinner').first()

        if dinner_exists is None:

            current_meal = Current_Meal(
                recipe_id=recipe_id,
                app_user_id=current_user.id,
                day_number=0,
                meal='dinner',
                active_ind=True,
                insert_datetime=datetime.now()
            )
            db.session.add(current_meal)
            db.session.flush()
            db.session.commit()

    
    # If user selected to remove recipe to meal plan, update table
    elif status == 'unchecked':
        db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).update(dict(active_ind=False))

        db.session.flush()
        db.session.commit()

    return render_template('all_recipes.html')


# Define route for manually removing BREAKFAST recipe from meal plan
@bp.route('/_remove_bfast_meal_plan', methods=['GET', 'POST'])
@login_required
def _remove_bfast_meal_plan():
    recipe_id = request.form.get('recipe_id')

    db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='breakfast').update(dict(active_ind=False))

    db.session.flush()
    db.session.commit()

    return render_template('meal_plan.html')


# Define route for manually removing LUNCH recipe from meal plan
@bp.route('/_remove_lunch_meal_plan', methods=['GET', 'POST'])
@login_required
def _remove_lunch_meal_plan():
    recipe_id = request.form.get('recipe_id')

    db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='lunch').update(dict(active_ind=False))

    db.session.flush()
    db.session.commit()

    return render_template('meal_plan.html')


# Define route for manually removing DINNER recipe from meal plan
@bp.route('/_remove_dinner_meal_plan', methods=['GET', 'POST'])
@login_required
def _remove_dinner_meal_plan():
    recipe_id = request.form.get('recipe_id')

    db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='dinner').update(dict(active_ind=False))

    db.session.flush()
    db.session.commit()

    return render_template('meal_plan.html')


# Define route for manually adding recipe to favorites
@bp.route('/_favorite', methods=['GET', 'POST'])
@login_required
def _favorite():
    status = request.form.get('status')
    recipe_id = request.form.get('recipe_id')

    # If user selected to add recipe to favorites, update table
    if status == 'checked':
        if db.session.query(Favorite_Recipe).filter(Favorite_Recipe.app_user_id==current_user.id).filter(Favorite_Recipe.recipe_id==recipe_id).first() == None:
            favorite_recipe = Favorite_Recipe(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            owner_ind=True,
                            insert_datetime=datetime.now()
                        )

            db.session.add(favorite_recipe)
            db.session.flush()
            db.session.commit()

        favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe).join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id).filter(Favorite_Recipe.app_user_id==current_user.id).filter(Recipe.recipe_deleted==None)).order_by(Recipe.recipe_name).all()

        fav_length = len(favorite_recipe_list)

        if fav_length != 0:
            fav_exists = True
        else:
            fav_exists = False 

    # If user selected to remove recipe from favorites, update table
    elif status == 'unchecked':
        db.session.query(Favorite_Recipe).filter(Favorite_Recipe.app_user_id==current_user.id).filter(Favorite_Recipe.recipe_id==recipe_id).delete()

        db.session.flush()
        db.session.commit()

        favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe).join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id).filter(Favorite_Recipe.app_user_id==current_user.id).filter(Recipe.recipe_deleted==None)).order_by(Recipe.recipe_name).all()

        fav_length = len(favorite_recipe_list)

        if fav_length != 0:
            fav_exists = True
        else:
            fav_exists = False 

    return render_template('all_recipes.html', favorite_recipe_list=favorite_recipe_list, fav_length=fav_length, fav_exists=fav_exists)


# Define route for deleting shopping list items
@bp.route('/_del_shopping_list_items', methods=['GET', 'POST'])
@login_required
def _del_shopping_list_items():
    s_list_id = request.form.get('s_list_id')

    # Delete value from database
    Shopping_List.query.filter_by(shopping_list_id=s_list_id).delete()

    db.session.flush()
    db.session.commit()

    # Query for shopping list items
    shop_list = (db.session.query(
        Shopping_List, 
        Recipe
    ).join(
        Recipe, Recipe.recipe_id==Shopping_List.recipe_id
    ).filter(
        Shopping_List.app_user_id==current_user.id
    ).order_by(Shopping_List.item_sort).all())

    return render_template('shopping_list.html', shop_list=shop_list)



# Define route for page to manually add recipes
@bp.route('/add', methods=['GET', 'POST'])
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
                recipe_image_url=None,
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

            # Write errors to APP_ERROR table
            app_error = App_Error(
                app_user_id=current_user.id,
                insert_datetime=datetime.now(),
                error_val=str(e)
            )
            db.session.add(app_error)
            db.session.flush()
            db.session.commit()
            

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


        # Render recipe_confirm.html template after recipe is written to DB    
        return(render_template('recipe_confirm.html', recipe_id=recipe.recipe_id, recipe_name=request.form['recipe_name']))

    # When not posting form, render the add.html template (main page for this route)
    #return render_template('add.html', output=output)
    return render_template('add.html')


# Define route for page to upload images to existing recipes
@bp.route('/upload_image/<recipe_id>', methods=['GET', 'POST'])
@login_required
def upload_image(recipe_id):
    output = []
    recipe = db.session.query(Recipe).filter_by(recipe_id=recipe_id).join(App_User).first()


    # If user submits data on input form, write to DB
    admins = (db.session.query(App_User).filter_by(admin=True).all())
    admins_list = [r.id for r in admins]
    if request.method == "POST" and ((recipe.created_by == current_user.id) or 
    (current_user.id in admins_list)):
        error=""
        # Clean image input and upload to AWS S3
        try:
            uploaded_file = request.files['file']
            filename_sec = secure_filename(uploaded_file.filename)
            if filename_sec != '':
                file_ext_base = os.path.splitext(filename_sec)[1]
                if file_ext_base == '.jpeg':
                    file_ext = '.jpg'
                else:
                    file_ext = file_ext_base

                if file_ext in current_app.config['UPLOAD_EXTENSIONS'] and \
                        file_ext == validate_image(uploaded_file.stream):
                        # Generate unique file name
                        filename = str(uuid4()) + file_ext
                        uploaded_file.save(os.path.join(current_app.config['UPLOAD_PATH'], filename))
                        image_url = upload_file(f"uploads/{filename}", BUCKET)

                        db.session.query(Recipe).filter_by(recipe_id=recipe_id).update(dict(recipe_image_url=image_url))

                        db.session.flush()
                        db.session.commit()
                else:
                    print("WHAT THE F")

            else:
                error = "Invalid image upload. Images must be a maximum size of 1024x1024 and one of the following types: .JPG or .PNG"
                return render_template('error.html', error=error)
   

        except Exception as e:
            output.append("Application encountered an error, and the image was not uploaded. Better luck in the future!")
            output.append(str(e))
            print(str(e))
            return render_template('error.html', error=e)

        # Render recipe_confirm.html template after image URL is written to DB    
        return(render_template('recipe_confirm.html', recipe_id=recipe.recipe_id, error=error, recipe_name=recipe.recipe_name))


    # When not posting form, render the upload_image.html template (main page for this route)
    return render_template('upload_image.html', recipe=recipe)



# Define route for page to modify existing recipes
@bp.route('/edit/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    output = []
    recipe = db.session.query(Recipe).filter_by(recipe_id=recipe_id).join(App_User).first()

    ingredient_list = Ingredient.query.filter_by(recipe_id=recipe_id)
    step_list = Recipe_Step.query.filter_by(recipe_id=recipe_id)

    #len_i = len(ingredient_list)

    # If user submits data on input form, write to DB
    admins = (db.session.query(App_User).filter_by(admin=True).all())
    admins_list = [r.id for r in admins]
    if request.method == "POST" and ((recipe.created_by == current_user.id) or 
    (current_user.id in admins_list)):
        error=""
        try:

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


                recipe.recipe_name=request.form['recipe_name']
                recipe.recipe_desc=request.form['recipe_desc']
                recipe.recipe_prep_time=prep_time
                recipe.recipe_cook_time=cook_time
                recipe.recipe_total_time=total_time
                recipe.serving_size=request.form['serving_size']
                recipe.recipe_url=manual_input_clean_url
                recipe.recipe_image_url=recipe.recipe_image_url
                recipe.diet_vegan=diet_vegan_input
                recipe.diet_vegetarian=diet_vegetarian_input
                recipe.diet_gluten=diet_gluten_input
                recipe.meal_breakfast=meal_breakfast_input
                recipe.meal_lunch=meal_lunch_input
                recipe.meal_dinner=meal_dinner_input
                # Below line ensures that ownership of the recipe does not transfer to Admin
                recipe.created_by=recipe.created_by
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

                # Write errors to APP_ERROR table
                app_error = App_Error(
                    app_user_id=current_user.id,
                    insert_datetime=datetime.now(),
                    error_val=str(e)
                )
                db.session.add(app_error)
                db.session.flush()
                db.session.commit()

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

                    # Write errors to APP_ERROR table
                    app_error = App_Error(
                        app_user_id=current_user.id,
                        insert_datetime=datetime.now(),
                        error_val=str(e)
                    )
                    db.session.add(app_error)
                    db.session.flush()
                    db.session.commit()


            # Render recipe_confirm.html template after recipe is written to DB    
            return(render_template('recipe_confirm.html', recipe_id=recipe.recipe_id, error=error, recipe_name=request.form['recipe_name']))

        except Exception as e:
            return render_template('error.html', error=e)

    # When not posting form, render the edit_recipe.html template (main page for this route)
    return render_template('edit_recipe.html', recipe=recipe, ingredient_list=ingredient_list, step_list=step_list)




# Define route to auto import / scrape recipe from external website
@bp.route('/auto_import', methods=['GET', 'POST'])
@login_required
def auto_import():
    output = []
    # If user inputs URL, scrape website for recipe data and write to DB:
    if request.method == "POST":

        try:
            
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


            # Scrape external website and clean data for write to the DB
            try:
                url_input = request.form['recipe_url']
                auto_import_clean_url = clean(url_input)
                scraper = scrape_me(url_input, wild_mode=True)
                yields = scraper.yields()
            except Exception as e:
                output.append("Recipe didn't scrape")
                # Write errors to APP_ERROR table
                app_error = App_Error(
                    app_user_id=current_user.id,
                    insert_datetime=datetime.now(),
                    error_val=str(e)
                )
                db.session.add(app_error)
                db.session.flush()
                db.session.commit()

            try:
                clean_yields = re.sub('[^0-9]','', yields)
                if clean_yields == None:
                    clean_yields = 0
                elif clean_yields == '':
                    clean_yields = 0
            except:
                clean_yields = 0
                

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
                    recipe_image_url=None,
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

                
            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
                output.append(str(e))

                # Write errors to APP_ERROR table
                app_error = App_Error(
                    app_user_id=current_user.id,
                    insert_datetime=datetime.now(),
                    error_val=str(e)
                )
                db.session.add(app_error)
                db.session.flush()
                db.session.commit()


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

                    # Write errors to APP_ERROR table
                    app_error = App_Error(
                        app_user_id=current_user.id,
                        insert_datetime=datetime.now(),
                        error_val=str(e)
                    )
                    db.session.add(app_error)
                    db.session.flush()
                    db.session.commit()

            # Insert data to RECIPE_STEP table
            instructions = scraper.instructions().split('\n')
            counter = 1
            for step in instructions:
                try:
                    recipe_step = Recipe_Step(
                        recipe_id=recipe.recipe_id,
                        step_order=counter,
                        step_desc=step,
                        insert_datetime=datetime.now()
                    )
                    counter += 1
                    db.session.add(recipe_step)
                    db.session.flush()
                    db.session.commit()
                # Return error if database write was unsuccessful
                except Exception as e:
                    db.session.rollback()
                    output.append("Application encountered an error, and the instructions didn't write to the database. Better luck in the future!")
                    output.append(str(e))

                    # Write errors to APP_ERROR table
                    app_error = App_Error(
                        app_user_id=current_user.id,
                        insert_datetime=datetime.now(),
                        error_val=str(e)
                    )
                    db.session.add(app_error)
                    db.session.flush()
                    db.session.commit()

                    # BELOW LINES USED FOR TROUBLESHOOTING IMPORT ISSUES
                    # error = 'This website is not supported at this time. Please manually add this recipe, and use the Auto Import function for one of the supported websites below.'

                    # return render_template("auto_import.html", error=error)


            # Insert data to FAVORITE_RECIPE table
            try:
                if request.form['mark_fav'] == 'fav':
                    favorite_recipe = Favorite_Recipe(
                        recipe_id=recipe.recipe_id,
                        app_user_id=current_user.id,
                        owner_ind=True,
                        insert_datetime=datetime.now()
                    )

                    db.session.add(favorite_recipe)
                    db.session.flush()
                    db.session.commit()

            except Exception as e:
                db.session.rollback()
                output.append("Application encountered an error, and the recipe was not marked as a favorite. Better luck in the future!")
                output.append(str(e))

                # Write errors to APP_ERROR table
                app_error = App_Error(
                    app_user_id=current_user.id,
                    insert_datetime=datetime.now(),
                    error_val=str(e)
                )
                db.session.add(app_error)
                db.session.flush()
                db.session.commit()


            # Render recipe_confirm.html template after recipe is written to DB
            return(render_template('recipe_confirm.html', recipe_id=recipe.recipe_id, recipe_name=scraper.title(), output=output))

            
        except Exception as e:
            error = 'This website is not supported at this time. Please manually add this recipe, and use the Auto Import function for one of the supported websites below.'
            
            # Write errors to APP_ERROR table
            app_error = App_Error(
                app_user_id=current_user.id,
                insert_datetime=datetime.now(),
                error_val=str(e)
            )
            db.session.add(app_error)
            db.session.flush()
            db.session.commit()

            return render_template("auto_import.html", error=error)

            

    # When not posting form, render the auto_import.html template (main page for this route)
    return render_template("auto_import.html", output=output)


# Define route for page to view all recipes
@bp.route('/all_recipes', methods=['GET', 'POST'])
@login_required
def all_recipes():
    # Your favorite recipes (created both by you and others)
    favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id)) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        # .filter(Favorite_Recipe.app_user_id==current_user.id) \
        # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
        .filter(Recipe.recipe_deleted==None)) \
        .order_by(Recipe.recipe_name) \
        .all()

    fav_length = len(favorite_recipe_list)

    if fav_length != 0:
        fav_exists = True
    else:
        fav_exists = False 


    # Recipes created by you
    your_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .filter(Recipe.created_by==current_user.id) \
        # .filter((Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None)) \
        # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
        .filter(Recipe.recipe_deleted==None)) \
        .order_by(Recipe.recipe_name) \
        .all()

    your_length = len(your_recipe_list)

    if your_length != 0:
        your_exists = True
    else:
        your_exists = False 

    
    # Editor's Picks recipes (recipes favorited by Admin)
    editor_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==1)) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        # .filter(Favorite_Recipe.app_user_id==1) \
        # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
        .filter(Recipe.recipe_deleted==None)) \
        .order_by(Recipe.recipe_name) \
        .all()

    editor_length = len(editor_recipe_list)

    if editor_length != 0:
        editor_exists = True
    else:
        editor_exists = False 


    # Recipes created by others
    other_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .filter(Recipe.created_by!=current_user.id) \
        # .filter((Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None)) \
        # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
        .filter(Recipe.recipe_deleted==None)) \
        .order_by(Recipe.recipe_name) \
        .all()
    
    other_length = len(other_recipe_list)

    if other_length != 0:
        other_exists = True
    else:
        other_exists = False 


    if request.method == "POST":
        error = ""
        output = []
        try:
    
            # User selects button to add respective meal to their current meal plan
            if ("fav_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form):

                recipe_id = request.form['recipe_id']


                # If recipe is categorized as a breakfast recipe, add to Meal Plan as a breakfast meal
                if (db.session.query(Recipe.meal_breakfast).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    breakfast_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='breakfast').first()

                    if breakfast_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='breakfast',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a lunch recipe, add to Meal Plan as a lunch meal
                if (db.session.query(Recipe.meal_lunch).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    lunch_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='lunch').first()

                    if lunch_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='lunch',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a dinner recipe, add to Meal Plan as a dinner meal
                if (db.session.query(Recipe.meal_dinner).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    dinner_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='dinner').first()

                    if dinner_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='dinner',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()


    
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
            print(output)

            # Write errors to APP_ERROR table
            app_error = App_Error(
                app_user_id=current_user.id,
                insert_datetime=datetime.now(),
                error_val=str(e)
            )
            db.session.add(app_error)
            db.session.flush()
            db.session.commit()


    # Render the all_recipes.html template (main page for this route)
    return render_template("all_recipes.html", favorite_recipe_list=favorite_recipe_list, your_recipe_list=your_recipe_list, editor_recipe_list=editor_recipe_list, other_recipe_list=other_recipe_list, fav_exists=fav_exists, your_exists=your_exists, editor_exists=editor_exists, other_exists=other_exists, fav_length=fav_length, your_length=your_length, editor_length=editor_length, other_length=other_length)


# Define route for page to view your favorite recipes
@bp.route('/recipe_list_favorites', methods=['GET', 'POST'])
@login_required
def recipe_list_favorites():
    # Your favorite recipes (created both by you and others)
    favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id)) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .filter(Recipe.recipe_deleted==None)) \
        .order_by(Recipe.recipe_name) \
        .all()

    fav_length = len(favorite_recipe_list)

    if fav_length != 0:
        fav_exists = True
    else:
        fav_exists = False 


    if request.method == "POST":
        error = ""
        output = []
        try:
    
            # User selects button to add respective meal to their current meal plan
            if ("fav_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form):

                recipe_id = request.form['recipe_id']


                # If recipe is categorized as a breakfast recipe, add to Meal Plan as a breakfast meal
                if (db.session.query(Recipe.meal_breakfast).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    breakfast_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='breakfast').first()

                    if breakfast_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='breakfast',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a lunch recipe, add to Meal Plan as a lunch meal
                if (db.session.query(Recipe.meal_lunch).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    lunch_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='lunch').first()

                    if lunch_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='lunch',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a dinner recipe, add to Meal Plan as a dinner meal
                if (db.session.query(Recipe.meal_dinner).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    dinner_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='dinner').first()

                    if dinner_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='dinner',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()


    
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
            print(output)

            # Write errors to APP_ERROR table
            app_error = App_Error(
                app_user_id=current_user.id,
                insert_datetime=datetime.now(),
                error_val=str(e)
            )
            db.session.add(app_error)
            db.session.flush()
            db.session.commit()


    # Render the recipe_list_favorites.html template (main page for this route)
    return render_template("recipe_list_favorites.html", favorite_recipe_list=favorite_recipe_list, fav_exists=fav_exists, fav_length=fav_length)


# Define route for page to view your uploaded recipes
@bp.route('/recipe_list_yours', methods=['GET', 'POST'])
@login_required
def recipe_list_yours():

    # Recipes created by you
    your_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .filter(Recipe.created_by==current_user.id) \
        # .filter((Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None)) \
        # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
        .filter(Recipe.recipe_deleted==None)) \
        .order_by(Recipe.recipe_name) \
        .all()

    your_length = len(your_recipe_list)

    if your_length != 0:
        your_exists = True
    else:
        your_exists = False 


    if request.method == "POST":
        error = ""
        output = []
        try:
    
            # User selects button to add respective meal to their current meal plan
            if ("fav_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form):

                recipe_id = request.form['recipe_id']


                # If recipe is categorized as a breakfast recipe, add to Meal Plan as a breakfast meal
                if (db.session.query(Recipe.meal_breakfast).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    breakfast_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='breakfast').first()

                    if breakfast_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='breakfast',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a lunch recipe, add to Meal Plan as a lunch meal
                if (db.session.query(Recipe.meal_lunch).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    lunch_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='lunch').first()

                    if lunch_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='lunch',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a dinner recipe, add to Meal Plan as a dinner meal
                if (db.session.query(Recipe.meal_dinner).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    dinner_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='dinner').first()

                    if dinner_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='dinner',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()


    
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
            print(output)

            # Write errors to APP_ERROR table
            app_error = App_Error(
                app_user_id=current_user.id,
                insert_datetime=datetime.now(),
                error_val=str(e)
            )
            db.session.add(app_error)
            db.session.flush()
            db.session.commit()


    # Render the recipe_list_yours.html template (main page for this route)
    return render_template("recipe_list_yours.html", your_recipe_list=your_recipe_list, your_exists=your_exists, your_length=your_length)


# Define route for page to view editor's picks recipes
@bp.route('/recipe_list_editor', methods=['GET', 'POST'])
@login_required
def recipe_list_editor():
    # Editor's Picks recipes (recipes favorited by Admin)
    editor_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==1)) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        # .filter(Favorite_Recipe.app_user_id==1) \
        # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
        .filter(Recipe.recipe_deleted==None)) \
        .order_by(Recipe.recipe_name) \
        .all()

    editor_length = len(editor_recipe_list)

    if editor_length != 0:
        editor_exists = True
    else:
        editor_exists = False 


    if request.method == "POST":
        error = ""
        output = []
        try:
    
            # User selects button to add respective meal to their current meal plan
            if ("fav_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form):

                recipe_id = request.form['recipe_id']


                # If recipe is categorized as a breakfast recipe, add to Meal Plan as a breakfast meal
                if (db.session.query(Recipe.meal_breakfast).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    breakfast_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='breakfast').first()

                    if breakfast_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='breakfast',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a lunch recipe, add to Meal Plan as a lunch meal
                if (db.session.query(Recipe.meal_lunch).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    lunch_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='lunch').first()

                    if lunch_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='lunch',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a dinner recipe, add to Meal Plan as a dinner meal
                if (db.session.query(Recipe.meal_dinner).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    dinner_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='dinner').first()

                    if dinner_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='dinner',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()


    
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
            print(output)

            # Write errors to APP_ERROR table
            app_error = App_Error(
                app_user_id=current_user.id,
                insert_datetime=datetime.now(),
                error_val=str(e)
            )
            db.session.add(app_error)
            db.session.flush()
            db.session.commit()


    # Render the recipe_list_editor.html template (main page for this route)
    return render_template("recipe_list_editor.html", editor_recipe_list=editor_recipe_list, editor_exists=editor_exists, editor_length=editor_length)


# Define route for page to view recipes uploaded by others
@bp.route('/recipe_list_others', methods=['GET', 'POST'])
@login_required
def recipe_list_others():
    
    # Recipes created by others
    other_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .filter(Recipe.created_by!=current_user.id) \
        # .filter((Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None)) \
        # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
        .filter(Recipe.recipe_deleted==None)) \
        .order_by(Recipe.recipe_name) \
        .all()
    
    other_length = len(other_recipe_list)

    if other_length != 0:
        other_exists = True
    else:
        other_exists = False 


    if request.method == "POST":
        error = ""
        output = []
        try:
    
            # User selects button to add respective meal to their current meal plan
            if ("fav_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form):

                recipe_id = request.form['recipe_id']


                # If recipe is categorized as a breakfast recipe, add to Meal Plan as a breakfast meal
                if (db.session.query(Recipe.meal_breakfast).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    breakfast_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='breakfast').first()

                    if breakfast_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='breakfast',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a lunch recipe, add to Meal Plan as a lunch meal
                if (db.session.query(Recipe.meal_lunch).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    lunch_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='lunch').first()

                    if lunch_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='lunch',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a dinner recipe, add to Meal Plan as a dinner meal
                if (db.session.query(Recipe.meal_dinner).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    dinner_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='dinner').first()

                    if dinner_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='dinner',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()


    
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
            print(output)

            # Write errors to APP_ERROR table
            app_error = App_Error(
                app_user_id=current_user.id,
                insert_datetime=datetime.now(),
                error_val=str(e)
            )
            db.session.add(app_error)
            db.session.flush()
            db.session.commit()


    # Render the recipe_list_others.html template (main page for this route)
    return render_template("recipe_list_others.html", other_recipe_list=other_recipe_list, other_exists=other_exists, other_length=other_length)



# Define route for page to view all recipes
""" @bp.route('/all_recipes', methods=['GET', 'POST'])
@login_required
def all_recipes():
    # All recipes list (created both by you and others)
    all_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id), isouter=True) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .filter(Recipe.recipe_deleted==None)) \
        .order_by(Recipe.recipe_name) \
        .all()

    recipe_list_length = len(all_recipe_list)

    if recipe_list_length != 0:
        recipe_list_exists = True
    else:
        recipe_list_exists = False 


    if request.method == "POST":
        error = ""
        output = []
        try:
    
            # User selects button to add respective meal to their current meal plan
            if ("fav_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form):

                recipe_id = request.form['recipe_id']


                # If recipe is categorized as a breakfast recipe, add to Meal Plan as a breakfast meal
                if (db.session.query(Recipe.meal_breakfast).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    breakfast_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='breakfast').first()

                    if breakfast_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='breakfast',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a lunch recipe, add to Meal Plan as a lunch meal
                if (db.session.query(Recipe.meal_lunch).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    lunch_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='lunch').first()

                    if lunch_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='lunch',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()

                # If recipe is categorized as a dinner recipe, add to Meal Plan as a dinner meal
                if (db.session.query(Recipe.meal_dinner).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

                    dinner_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(app_user_id=current_user.id).filter_by(active_ind=True).filter_by(meal='dinner').first()

                    if dinner_exists is None:

                        current_meal = Current_Meal(
                            recipe_id=recipe_id,
                            app_user_id=current_user.id,
                            day_number=0,
                            meal='dinner',
                            active_ind=True,
                            insert_datetime=datetime.now()
                        )
                        db.session.add(current_meal)
                        db.session.flush()
                        db.session.commit()


    
        except Exception as e:
            db.session.rollback()
            output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
            output.append(str(e))
            print(output)

            # Write errors to APP_ERROR table
            app_error = App_Error(
                app_user_id=current_user.id,
                insert_datetime=datetime.now(),
                error_val=str(e)
            )
            db.session.add(app_error)
            db.session.flush()
            db.session.commit()


    # Render the all_recipes.html template (main page for this route)
    return render_template("all_recipes.html", all_recipe_list=all_recipe_list, recipe_list_exists=recipe_list_exists, recipe_list_length=recipe_list_length)
 """

# Define route for recipe search
@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():

    if request.method == "POST":

        search_terms = request.form['search_terms']

        # Split the search terms into individual list items
        split_search_terms = search_terms.split()

        # Query database for search terms. Only query for the first 5 words.
        new_split_search_terms = []
        for word in split_search_terms:
            search_word = "%" + word.lower() + "%"
            new_split_search_terms.append(search_word)

        # Ensure that list of words length is >= 5 so that queries execute successfully
        missing_items = 5 - len(new_split_search_terms)
        if missing_items > 0:
            for x in range(5):
                new_split_search_terms.append('abcxyz')

            
        print("SEARCH TERMS")
        print(new_split_search_terms)


        # search_results = db.session.query(Recipe).filter(or_(Recipe.recipe_name.like(new_split_search_terms[0]), Recipe.recipe_name.like(new_split_search_terms[1]), Recipe.recipe_name.like(new_split_search_terms[2]), Recipe.recipe_name.like(new_split_search_terms[3]), Recipe.recipe_name.like(new_split_search_terms[4])))

        search_results = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .filter(Recipe.recipe_deleted==None)) \
        .filter(or_(func.lower(Recipe.recipe_name).like(new_split_search_terms[0]), func.lower(Recipe.recipe_name).like(new_split_search_terms[1]), func.lower(Recipe.recipe_name).like(new_split_search_terms[2]), func.lower(Recipe.recipe_name).like(new_split_search_terms[3]), func.lower(Recipe.recipe_name).like(new_split_search_terms[4]))) \
        .order_by(Recipe.recipe_name) \
        .all()

        search_results_length = len(search_results)

        if search_results_length != 0:
            search_results_exist = True
        else:
            search_results_exist = False 

        print("SEARCH RESULTS")
        print(search_results)

        return render_template('search.html', search_results=search_results, search_results_exist=search_results_exist, search_results_length=search_results_length, search_terms=search_terms)

    else:
        return render_template('search.html')


# Define route for page to view detailed info about one recipe
@bp.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def recipe_detail(recipe_id):

    # Get recipe details
    recipe = db.session.query(Recipe).filter_by(recipe_id=recipe_id).join(App_User).first()

    # Identify if recipe is on curent meal plan
    current = db.session.query(Current_Meal) \
        .filter_by(recipe_id=recipe_id) \
        .filter_by(app_user_id=current_user.id) \
        .first()


    # Determine if recipe is one of the user's favorite recipes
    favorite = db.session.query(Favorite_Recipe) \
        .filter_by(recipe_id=recipe_id) \
        .filter_by(app_user_id=current_user.id) \
        .first()

    # Get ingredient list for recipe
    ingredient_list = Ingredient \
        .query \
        .filter_by(recipe_id=recipe_id) \
        .order_by(Ingredient.ingredient_id)

    # Get step list for recipe
    step_list = Recipe_Step \
        .query \
        .filter_by(recipe_id=recipe_id) \
        .order_by(Recipe_Step.step_order)

    output = []
    if request.method == "POST":
        
        if "favorite_submit" in request.form:
            # If user selects 'add to favorites' button and the recipe is not a favorite, add the user/recipe combo to favorites table:
            if favorite == None:
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
                    print(output)

                    # Write errors to APP_ERROR table
                    app_error = App_Error(
                        app_user_id=current_user.id,
                        insert_datetime=datetime.now(),
                        error_val=str(e)
                    )
                    db.session.add(app_error)
                    db.session.flush()
                    db.session.commit()
        
            # If user selects 'add to favorites' button and the recipe is already a favorite, delete the user/recipe combo to favorites table:
            else:
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
                    print(output)

                    # Write errors to APP_ERROR table
                    app_error = App_Error(
                        app_user_id=current_user.id,
                        insert_datetime=datetime.now(),
                        error_val=str(e)
                    )
                    db.session.add(app_error)
                    db.session.flush()
                    db.session.commit()


        # Route for deleting recipe
        admins = (db.session.query(App_User).filter_by(admin=True).all())
        admins_list = [r.id for r in admins]
        if "delete_submit" in request.form and ((recipe.created_by == current_user.id) or 
        (current_user.id in admins_list)):
            db.session.query(Recipe).filter_by(recipe_id=recipe_id).update(dict(recipe_deleted=True))

            db.session.flush()
            db.session.commit()

            # After deleting, render the all_recipes.html template

            # Your favorite recipes (created both by you and others)
            favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
                .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id)) \
                .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
                # .filter(Favorite_Recipe.app_user_id==current_user.id) \
                # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
                .filter(Recipe.recipe_deleted==None)) \
                .order_by(Recipe.recipe_name) \
                .all()

            fav_length = len(favorite_recipe_list)

            if fav_length != 0:
                fav_exists = True
            else:
                fav_exists = False 


            # Recipes created by you
            your_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
                .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
                .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
                .filter(Recipe.created_by==current_user.id) \
                # .filter((Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None)) \
                # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
                .filter(Recipe.recipe_deleted==None)) \
                .order_by(Recipe.recipe_name) \
                .all()

            your_length = len(your_recipe_list)

            if your_length != 0:
                your_exists = True
            else:
                your_exists = False 

            
            # Editor's Picks recipes (recipes favorited by Admin)
            editor_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
                .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==1)) \
                .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
                # .filter(Favorite_Recipe.app_user_id==1) \
                # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
                .filter(Recipe.recipe_deleted==None)) \
                .order_by(Recipe.recipe_name) \
                .all()

            editor_length = len(editor_recipe_list)

            if editor_length != 0:
                editor_exists = True
            else:
                editor_exists = False 


            # Recipes created by others
            other_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
                .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
                .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
                .filter(Recipe.created_by!=current_user.id) \
                # .filter((Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None)) \
                # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
                .filter(Recipe.recipe_deleted==None)) \
                .order_by(Recipe.recipe_name) \
                .all()
            
            other_length = len(other_recipe_list)

            if other_length != 0:
                other_exists = True
            else:
                other_exists = False


            return render_template("all_recipes.html", favorite_recipe_list=favorite_recipe_list, your_recipe_list=your_recipe_list, editor_recipe_list=editor_recipe_list, other_recipe_list=other_recipe_list, fav_exists=fav_exists, your_exists=your_exists, editor_exists=editor_exists, other_exists=other_exists, fav_length=fav_length, your_length=your_length, editor_length=editor_length, other_length=other_length)


    # If user is the owner of the recipe, pass a flag to render the 'Edit' and 'Delete' buttons
    admins = (db.session.query(App_User).filter_by(admin=True).all())
    admins_list = [r.id for r in admins]
    if ((recipe.created_by == current_user.id) or (current_user.id in admins_list)):
        owner_ind = True
    else:
        owner_ind = False

    # Render the recipe_detail.html template (main page for this route)
    return render_template('recipe_detail.html', recipe=recipe, current=current, ingredient_list=ingredient_list, step_list=step_list, favorite=favorite, owner_ind=owner_ind)
    
    

