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

from app.models import Recipe, Ingredient, Recipe_Step, App_User, Current_Meal, User_Recipe, Favorite_Recipe, Shopping_List, App_Error, User_Link

from app.view_recipes import bp


# Define route for page to view your favorite recipes
@bp.route('/recipe_list_favorites', methods=['GET', 'POST'])
@login_required
def recipe_list_favorites():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    # Your favorite recipes (created both by you and others)
    favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.active_ind, User_Link) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id)) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .join(User_Link, (User_Link.combined_user_id==combined_user_id), isouter=True) \
        .filter(Recipe.recipe_deleted==False)) \
        .filter(User_Link.app_user_id==current_user.id) \
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
            if ("fav_meal_plan_submit" in request.form) or ("editor_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form) or ("all_meal_plan_submit" in request.form):

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
                            weekday_id=None,
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
                            weekday_id=None,
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
                            weekday_id=None,
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
    return render_template("view_recipes/recipe_list_favorites.html", favorite_recipe_list=favorite_recipe_list, fav_exists=fav_exists, fav_length=fav_length)


# Define route for page to view your uploaded recipes
@bp.route('/recipe_list_yours', methods=['GET', 'POST'])
@login_required
def recipe_list_yours():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    # Recipes created by you
    your_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.active_ind, User_Link) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .join(User_Link, (User_Link.combined_user_id==combined_user_id), isouter=True) \
        .filter(Recipe.created_by==current_user.id) \
        .filter(Recipe.recipe_deleted==False)) \
        .filter(User_Link.app_user_id==current_user.id) \
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
            if ("fav_meal_plan_submit" in request.form) or ("editor_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form) or ("all_meal_plan_submit" in request.form):

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
                            weekday_id=None,
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
                            weekday_id=None,
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
                            weekday_id=None,
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
    return render_template("view_recipes/recipe_list_yours.html", your_recipe_list=your_recipe_list, your_exists=your_exists, your_length=your_length)


# Define route for page to view editor's picks recipes
@bp.route('/recipe_list_editor', methods=['GET', 'POST'])
@login_required
def recipe_list_editor():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    # Editor's Picks recipes (recipes favorited by Admin)
    editor_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.active_ind, User_Link) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==1)) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .join(User_Link, (User_Link.combined_user_id==combined_user_id), isouter=True) \
        .filter(Recipe.recipe_deleted==False)) \
        .filter(User_Link.app_user_id==current_user.id) \
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
            if ("fav_meal_plan_submit" in request.form) or ("editor_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form) or ("all_meal_plan_submit" in request.form):

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
                            weekday_id=None,
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
                            weekday_id=None,
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
                            weekday_id=None,
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
    return render_template("view_recipes/recipe_list_editor.html", editor_recipe_list=editor_recipe_list, editor_exists=editor_exists, editor_length=editor_length)


# Define route for page to view recipes uploaded by others
@bp.route('/recipe_list_others', methods=['GET', 'POST'])
@login_required
def recipe_list_others():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))
    
    # Recipes created by others
    other_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.active_ind, User_Link) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
        .join(User_Link, (User_Link.combined_user_id==combined_user_id), isouter=True) \
        .filter(Recipe.created_by!=current_user.id) \
        # .filter((Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None)) \
        # .filter((Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None)) \
        .filter(Recipe.recipe_deleted==False)) \
        .filter(User_Link.app_user_id==current_user.id) \
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
            if ("fav_meal_plan_submit" in request.form) or ("editor_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form) or ("all_meal_plan_submit" in request.form):

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
                            weekday_id=None,
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
                            weekday_id=None,
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
                            weekday_id=None,
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
    return render_template("view_recipes/recipe_list_others.html", other_recipe_list=other_recipe_list, other_exists=other_exists, other_length=other_length)


# Define route for page to view all recipes
@bp.route('/recipe_list_all', methods=['GET', 'POST'])
@login_required
def recipe_list_all():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    # All recipes (created both by you and others)
    all_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.active_ind, User_Link) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.combined_user_id==combined_user_id), isouter=True) \
        .join(User_Link, (User_Link.combined_user_id==combined_user_id), isouter=True) \
        .filter(Recipe.recipe_deleted==False)) \
        .filter(User_Link.app_user_id==current_user.id) \
        .order_by(Recipe.recipe_name) \
        .all()

    all_length = len(all_recipe_list)

    if all_length != 0:
        all_exists = True
    else:
        all_exists = False 


    if request.method == "POST":
        error = ""
        output = []
        try:
    
            # User selects button to add respective meal to their current meal plan
            if ("fav_meal_plan_submit" in request.form) or ("editor_meal_plan_submit" in request.form) or ("your_meal_plan_submit" in request.form) or ("other_meal_plan_submit" in request.form) or ("all_meal_plan_submit" in request.form):

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
                            weekday_id=None,
                            active_ind=True,
                            insert_datetime=datetime.now(),
                            combined_user_id=combined_user_id
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
                            weekday_id=None,
                            active_ind=True,
                            insert_datetime=datetime.now(),
                            combined_user_id=combined_user_id
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
                            weekday_id=None,
                            active_ind=True,
                            insert_datetime=datetime.now(),
                            combined_user_id=combined_user_id
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


    # Render the recipe_list_all.html template (main page for this route)
    return render_template("view_recipes/recipe_list_all.html", all_recipe_list=all_recipe_list, all_exists=all_exists, all_length=all_length)


# Define route for recipe search
@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():

    if request.method == "POST":

        # Get combined_user_id
        combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

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


        search_results = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.active_ind, User_Link) \
        .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id) | (Favorite_Recipe.app_user_id==None), isouter=True) \
        .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.combined_user_id==combined_user_id), isouter=True) \
        .join(User_Link, (User_Link.combined_user_id==combined_user_id), isouter=True) \
        .filter(Recipe.recipe_deleted==False)) \
        .filter(or_(func.lower(Recipe.recipe_name).like(new_split_search_terms[0]), func.lower(Recipe.recipe_name).like(new_split_search_terms[1]), func.lower(Recipe.recipe_name).like(new_split_search_terms[2]), func.lower(Recipe.recipe_name).like(new_split_search_terms[3]), func.lower(Recipe.recipe_name).like(new_split_search_terms[4]))) \
        .filter(User_Link.app_user_id==current_user.id) \
        .order_by(Recipe.recipe_name) \
        .all()

        search_results_length = len(search_results)

        if search_results_length != 0:
            search_results_exist = True
        else:
            search_results_exist = False 

        return render_template('view_recipes/search.html', search_results=search_results, search_results_exist=search_results_exist, search_results_length=search_results_length, search_terms=search_terms)

    else:
        return render_template('view_recipes/search.html')


# Define route for page to view detailed info about one recipe
@bp.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def recipe_detail(recipe_id):

    # Get recipe details
    recipe = db.session.query(Recipe).filter_by(recipe_id=recipe_id).join(App_User).first()

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    # Identify admins
    admins = (db.session.query(App_User).filter_by(admin=True).all())
    admins_list = [r.id for r in admins]
    if current_user.id in admins_list:
        admin_user = True
    else:
        admin_user = False

    # Identify if recipe is on curent meal plan
    current = db.session.query(Current_Meal) \
        .filter_by(recipe_id=recipe_id) \
        .filter_by(combined_user_id=combined_user_id) \
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

                    return render_template('view_recipes/recipe_detail.html', recipe=recipe, ingredient_list=ingredient_list, step_list=step_list, favorite=favorite)

                    
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

                    return render_template('view_recipes/recipe_detail.html', recipe=recipe, ingredient_list=ingredient_list, step_list=step_list, favorite=favorite)
                
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

        if "cert_submit" in request.form and current_user.id in admins_list:

            # If admin selects 'certify recipe' button, update the recipes table:
            if recipe.editor_certified != True:
                db.session.query(Recipe).filter_by(recipe_id=recipe_id).update(dict(editor_certified=True))

            else:
                db.session.query(Recipe).filter_by(recipe_id=recipe_id).update(dict(editor_certified=False))

            db.session.flush()
            db.session.commit()

            return redirect(url_for('view_recipes.recipe_detail', recipe_id=recipe_id))

                

        # Route for deleting recipe
        admins = (db.session.query(App_User).filter_by(admin=True).all())
        admins_list = [r.id for r in admins]
        if "delete_submit" in request.form and ((recipe.created_by == current_user.id) or 
        (current_user.id in admins_list)):
            db.session.query(Recipe).filter_by(recipe_id=recipe_id).update(dict(recipe_deleted=True))

            db.session.flush()
            db.session.commit()


            # After deleting, render the recipe_list_favorites.html template
            # Your favorite recipes (created both by you and others)
            favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe, Current_Meal.recipe_id, Current_Meal.app_user_id, Current_Meal.active_ind) \
                .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==current_user.id)) \
                .join(Current_Meal, (Recipe.recipe_id==Current_Meal.recipe_id) & (Current_Meal.active_ind==True) & (Current_Meal.app_user_id==current_user.id) | (Current_Meal.app_user_id==None), isouter=True) \
                .filter(Recipe.recipe_deleted==False)) \
                .order_by(Recipe.recipe_name) \
                .all()

            fav_length = len(favorite_recipe_list)

            if fav_length != 0:
                fav_exists = True
            else:
                fav_exists = False
            
            return render_template("view_recipes/recipe_list_favorites.html", favorite_recipe_list=favorite_recipe_list, fav_exists=fav_exists, fav_length=fav_length)


    # If user is the owner of the recipe, pass a flag to render the 'Edit' and 'Delete' buttons
    admins = (db.session.query(App_User).filter_by(admin=True).all())
    admins_list = [r.id for r in admins]
    if ((recipe.created_by == current_user.id) or (current_user.id in admins_list)):
        owner_ind = True
    else:
        owner_ind = False

    # Render the recipe_detail.html template (main page for this route)
    return render_template('view_recipes/recipe_detail.html', recipe=recipe, current=current, ingredient_list=ingredient_list, step_list=step_list, favorite=favorite, owner_ind=owner_ind, admin_user=admin_user)
 