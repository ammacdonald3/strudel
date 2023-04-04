from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort, send_from_directory, current_app
import flask_sqlalchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
from sqlalchemy import or_, func
import random
import sys

from flask import current_app as app

from app import db

from app.models import Recipe, Ingredient, Recipe_Step, App_User, Current_Meal, User_Recipe, Favorite_Recipe, Shopping_List, App_Error, User_Link

from app.meal_planning import bp


# Define route for meal selector page
@bp.route('/meal_selector', methods=['GET', 'POST'])
@login_required
def meal_selector():
    output = []
    if request.method == "POST":

        # Get combined_user_id
        combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))
        
        try:
            # Update user's current meal list to inactivate all meals
            db.session.query(Current_Meal).filter(Current_Meal.combined_user_id==combined_user_id).update(dict(active_ind=False), synchronize_session=False)

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
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's favorite lunch recipes
                lunch_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id) \
                    .filter(Favorite_Recipe.app_user_id==current_user.id) \
                    .filter(Recipe.meal_lunch==True) \
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's favorite dinner recipes
                dinner_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id) \
                    .filter(Favorite_Recipe.app_user_id==current_user.id) \
                    .filter(Recipe.meal_dinner==True) \
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

            
            # If user wants to generate plan from all recipes they uploaded
            elif request.form['recipe_source'] == 'you':

                # Retrieve a list of user's breakfast recipes
                bfast_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.created_by==current_user.id) \
                    .filter(Recipe.meal_breakfast==True) \
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's lunch recipes
                lunch_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.created_by==current_user.id) \
                    .filter(Recipe.meal_lunch==True) \
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's dinner recipes
                dinner_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.created_by==current_user.id) \
                    .filter(Recipe.meal_dinner==True) \
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()


            # If user wants to generate plan from the editor's picks
            elif request.form['recipe_source'] == 'editor':

                # Retrieve a list of editor's breakfast recipes
                bfast_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==1)) \
                    .filter(Recipe.meal_breakfast==True) \
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of editor's lunch recipes
                lunch_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==1)) \
                    .filter(Recipe.meal_lunch==True) \
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of editor's dinner recipes
                dinner_recipe_list = (db.session.query(Recipe, Favorite_Recipe) \
                    .join(Favorite_Recipe, (Recipe.recipe_id==Favorite_Recipe.recipe_id) & (Favorite_Recipe.app_user_id==1)) \
                    .filter(Recipe.meal_dinner==True) \
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()


            # If user wants to generate plan from all recipes in the app
            elif request.form['recipe_source'] == 'all':

                # Retrieve a list of user's breakfast recipes
                bfast_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.meal_breakfast==True) \
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's lunch recipes
                lunch_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.meal_lunch==True) \
                    .filter(Recipe.recipe_deleted==False)) \
                    .order_by(Recipe.recipe_name) \
                    .all()

                # Retrieve a list of user's dinner recipes
                dinner_recipe_list = (db.session.query(Recipe) \
                    .filter(Recipe.meal_dinner==True) \
                    .filter(Recipe.recipe_deleted==False)) \
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
                        weekday_id=None,
                        active_ind=True,
                        insert_datetime=datetime.now(),
                        combined_user_id=combined_user_id
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
                        weekday_id=None,
                        active_ind=True,
                        insert_datetime=datetime.now(),
                        combined_user_id=combined_user_id
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
                        weekday_id=None,
                        active_ind=True,
                        insert_datetime=datetime.now(),
                        combined_user_id=combined_user_id
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
                        weekday_id=None,
                        active_ind=True,
                        insert_datetime=datetime.now(),
                        combined_user_id=combined_user_id
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
                        weekday_id=None,
                        active_ind=True,
                        insert_datetime=datetime.now(),
                        combined_user_id=combined_user_id
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
                        weekday_id=None,
                        active_ind=True,
                        insert_datetime=datetime.now(),
                        combined_user_id=combined_user_id
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
    return render_template('meal_planning/meal_selector.html', output=output)


# Define route for meal plan page
@bp.route('/meal_plan', methods=['GET', 'POST'])
@login_required
def meal_plan():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    # User manually adds a one-off meal
    if request.method == "POST":

        if "one-off-meal-proceed" in request.form:

            # Get recipe name
            one_off_meal = request.form['one-off-item-input']

            # Identify meal time
            input_meal = request.form['meal_choice']

            # Insert to Recipe table with deleted flag set
            recipe = Recipe(
                recipe_name=one_off_meal,
                recipe_desc=None,
                recipe_prep_time=None,
                recipe_cook_time=None,
                recipe_total_time=None,
                serving_size=None,
                recipe_url=None,
                recipe_image_url=None,
                diet_vegan=None,
                diet_vegetarian=None,
                diet_gluten=None,
                meal_breakfast=None,
                meal_lunch=None,
                meal_dinner=None,
                created_by=current_user.id,
                insert_datetime=datetime.now(),
                recipe_deleted=True,
                editor_certified=False
            )

            db.session.add(recipe)
            db.session.flush()
            db.session.commit()


            # Insert selected meals to Current_Meal table
            current_meal = Current_Meal(
                recipe_id=recipe.recipe_id,
                app_user_id=current_user.id,
                day_number=0,
                meal=input_meal,
                weekday_id=None,
                active_ind=True,
                insert_datetime=datetime.now(),
                combined_user_id=combined_user_id
            )

            db.session.add(current_meal)
            db.session.flush()
            db.session.commit()


    # Get list of user's selected breakfast meals
    selected_bfast_meals_list = (db.session.query(Recipe, Current_Meal, App_User).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).join(App_User, Current_Meal.app_user_id==App_User.id).filter(Current_Meal.combined_user_id==combined_user_id).filter(Current_Meal.active_ind==True).filter(Current_Meal.meal=='breakfast').order_by(Current_Meal.day_number)).all()

    bfast_length = len(selected_bfast_meals_list)

    if bfast_length != 0:
        bfast_exists = True
    else:
        bfast_exists = False 

    # Get list of user's selected lunch meals
    selected_lunch_meals_list = (db.session.query(Recipe, Current_Meal, App_User).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).join(App_User, Current_Meal.app_user_id==App_User.id).filter(Current_Meal.combined_user_id==combined_user_id).filter(Current_Meal.active_ind==True).filter(Current_Meal.meal=='lunch').order_by(Current_Meal.day_number)).all()

    lunch_length = len(selected_lunch_meals_list)

    if lunch_length != 0:
        lunch_exists = True
    else:
        lunch_exists = False 


    # Get list of user's selected dinner meals
    selected_dinner_meals_list = (db.session.query(Recipe, Current_Meal, App_User).join(Current_Meal, Recipe.recipe_id==Current_Meal.recipe_id).join(App_User, Current_Meal.app_user_id==App_User.id).filter(Current_Meal.combined_user_id==combined_user_id).filter(Current_Meal.active_ind==True).filter(Current_Meal.meal=='dinner').order_by(Current_Meal.day_number)).all()

    dinner_length = len(selected_dinner_meals_list)

    if dinner_length != 0:
        dinner_exists = True
    else:
        dinner_exists = False


    # Determine which card to render expanded by default
    if dinner_exists is True:
        priority_meal = "Dinner"
    elif lunch_exists is True:
        priority_meal = "Lunch"
    elif bfast_exists is True:
        priority_meal = "Breakfast"
    else:
        priority_meal = None


    return render_template('meal_planning/meal_plan.html', selected_bfast_meals_list=selected_bfast_meals_list, selected_lunch_meals_list=selected_lunch_meals_list, selected_dinner_meals_list=selected_dinner_meals_list,
    bfast_exists=bfast_exists,
    lunch_exists=lunch_exists,
    dinner_exists=dinner_exists,
    bfast_length=bfast_length,
    lunch_length=lunch_length,
    dinner_length=dinner_length,
    priority_meal=priority_meal
    )

    

# Define route for shopping list page
@bp.route('/shopping_list', methods=['GET', 'POST'])
@login_required
def shopping_list():
    output = []

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    if request.method == "POST":

        # Path for manually adding new shopping list items
        if "add_submit" in request.form:
            try:
                shopping_list_item = request.form['add_item']

                # Retrieve the current items in the shopping list
                shop_list = (db.session.query(
                    Shopping_List
                ).filter(
                    Shopping_List.combined_user_id==combined_user_id
                ).order_by(Shopping_List.item_sort).all())


                # Delete existing shopping list
                Shopping_List.query.filter_by(combined_user_id=combined_user_id).delete(synchronize_session="fetch")


                # Insert new item first
                shopping_list = Shopping_List(
                    item_desc=shopping_list_item,
                    recipe_id=None,
                    ingredient_id=None,
                    app_user_id=current_user.id,
                    item_sort=0,
                    checked_status=False,
                    insert_datetime=datetime.now(),
                    combined_user_id=combined_user_id
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
                        insert_datetime=item.insert_datetime,
                        combined_user_id=combined_user_id
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

        # Path for deleting checked items from shopping list:
        if "del_checked_submit" in request.form:
            try:

                # Delete checked shopping list
                Shopping_List.query.filter(Shopping_List.checked_status==True).filter_by(combined_user_id=combined_user_id).delete(synchronize_session="fetch")

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
        # This code block is placed here intentionally to allow user to delete auto-generated items in the same workflow as generating new items
        if "del_all_submit" in request.form or ("gen_with_delete_submit" in request.form):
            try:

                # Delete existing shopping list
                Shopping_List.query.filter_by(combined_user_id=combined_user_id).delete(synchronize_session="fetch")

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


        # Path for deleting auto-generated items from shopping list:
        if ("del_auto_submit" in request.form):
            try:

                # Delete existing shopping list
                Shopping_List.query.filter(Shopping_List.recipe_id.isnot(None)).filter_by(combined_user_id=combined_user_id).delete(synchronize_session="fetch")

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


        # Path for deleting custom-added items from shopping list:
        if "del_custom_submit" in request.form:
            try:

                # Delete existing shopping list
                Shopping_List.query.filter_by(combined_user_id=combined_user_id).filter_by(recipe_id=None).delete(synchronize_session="fetch")

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
        if ("gen_without_delete_submit" in request.form) or ("gen_with_delete_submit" in request.form) or ("gen_no_existing_items_submit" in request.form):
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
                shop_list = (db.session.query(Ingredient, Current_Meal).join(Current_Meal, Ingredient.recipe_id==Current_Meal.recipe_id).filter(Current_Meal.combined_user_id==combined_user_id).filter(Current_Meal.active_ind==True)).all()


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
                            insert_datetime=datetime.now(),
                            combined_user_id=combined_user_id
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


        

    # Query for shopping list items
    shop_list = (db.session.query(
        Shopping_List, 
        Recipe
    ).outerjoin(
        Recipe, Recipe.recipe_id==Shopping_List.recipe_id
    ).filter(
        Shopping_List.combined_user_id==combined_user_id
    ).order_by(Shopping_List.checked_status).order_by(Shopping_List.insert_datetime.desc()).all())

    
    return render_template('meal_planning/shopping_list.html', shop_list=shop_list)


# Define route for checking off shopping list items with ajax
@bp.route('/_shopping_list_items', methods=['GET', 'POST'])
@login_required
def _shopping_list_items():
    status = request.form.get('status')
    s_list_id = request.form.get('s_list_id')

    # If user checked an item, update DB to flag it as checked
    if status == 'checked':
        db.session.query(Shopping_List).filter(Shopping_List.shopping_list_id==s_list_id).update(dict(checked_status=True), synchronize_session=False)
    
    # If user unchecked an item, update DB to flag it as unchecked
    elif status == 'unchecked':
        db.session.query(Shopping_List).filter(Shopping_List.shopping_list_id==s_list_id).update(dict(checked_status=False), synchronize_session=False)
    
    db.session.flush()
    db.session.commit()

    # Query for shopping list items
    shop_list = (db.session.query(
        Shopping_List, 
        Recipe
    ).join(
        Recipe, Recipe.recipe_id==Shopping_List.recipe_id
    ).filter(
        Shopping_List.combined_user_id==combined_user_id
    ).order_by(Shopping_List.item_sort).all())

    return render_template('meal_planning/shopping_list.html', shop_list=shop_list)


# Define route for manually adding recipe to meal plan
@bp.route('/_meal_plan', methods=['GET', 'POST'])
@login_required
def _meal_plan():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    status = request.form.get('status')
    recipe_id = request.form.get('recipe_id')

    # If user selected to add recipe to meal plan, update table
    if status == 'checked':
        # If recipe is categorized as a breakfast recipe, add to Meal Plan as a breakfast meal
        if (db.session.query(Recipe.meal_breakfast).filter(Recipe.recipe_id==recipe_id)).scalar() == True:

            breakfast_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).filter_by(meal='breakfast').first()

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

            lunch_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).filter_by(meal='lunch').first()

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

            dinner_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).filter_by(meal='dinner').first()

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
    
    # If user selected to remove recipe to meal plan, update table
    elif status == 'unchecked':
        db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).update(dict(active_ind=False), synchronize_session=False)

        db.session.flush()
        db.session.commit()

    return render_template('view_recipes/recipe_list_all.html')


# Define route for clearing all items from meal plan
@bp.route('/_clear_meal_plan', methods=['GET','POST'])
@login_required
def _clear_meal_plan():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))
    
    # Inactivate all items from user's meal plan
    try:
        db.session.query(Current_Meal).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).update(dict(active_ind=False), synchronize_session=False)

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

    return render_template('meal_planning/meal_plan.html')


# Define route for manually adding BREAKFAST recipe to meal plan
@bp.route('/_meal_breakfast', methods=['GET', 'POST'])
@login_required
def _meal_breakfast():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    status = request.form.get('status')
    recipe_id = request.form.get('recipe_id')

    # If user selected to add recipe to meal plan, update table
    if status == 'checked':

        breakfast_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).filter_by(meal='breakfast').first()

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

    
    # If user selected to remove recipe to meal plan, update table
    elif status == 'unchecked':
        db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).update(dict(active_ind=False), synchronize_session=False)

        db.session.flush()
        db.session.commit()

    return render_template('view_recipes/recipe_list_all.html')


# Define route for manually adding LUNCH recipe to meal plan
@bp.route('/_meal_lunch', methods=['GET', 'POST'])
@login_required
def _meal_lunch():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    status = request.form.get('status')
    recipe_id = request.form.get('recipe_id')

    # If user selected to add recipe to meal plan, update table
    if status == 'checked':

        lunch_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).filter_by(meal='lunch').first()

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

    
    # If user selected to remove recipe to meal plan, update table
    elif status == 'unchecked':
        db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).update(dict(active_ind=False), synchronize_session=False)

        db.session.flush()
        db.session.commit()

    return render_template('view_recipes/recipe_list_all.html')


# Define route for manually adding DINNER recipe to meal plan
@bp.route('/_meal_dinner', methods=['GET', 'POST'])
@login_required
def _meal_dinner():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    status = request.form.get('status')
    recipe_id = request.form.get('recipe_id')

    # If user selected to add recipe to meal plan, update table
    if status == 'checked':

        dinner_exists = db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).filter_by(meal='dinner').first()

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

    
    # If user selected to remove recipe to meal plan, update table
    elif status == 'unchecked':
        db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).update(dict(active_ind=False), synchronize_session=False)

        db.session.flush()
        db.session.commit()

    return render_template('view_recipes/recipe_list_all.html')


# Define route for manually removing BREAKFAST recipe from meal plan
@bp.route('/_remove_bfast_meal_plan', methods=['GET', 'POST'])
@login_required
def _remove_bfast_meal_plan():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    recipe_id = request.form.get('recipe_id')

    db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).filter_by(meal='breakfast').update(dict(active_ind=False), synchronize_session=False)

    db.session.flush()
    db.session.commit()

    return render_template('meal_planning/meal_plan.html')


# Define route for manually removing LUNCH recipe from meal plan
@bp.route('/_remove_lunch_meal_plan', methods=['GET', 'POST'])
@login_required
def _remove_lunch_meal_plan():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    recipe_id = request.form.get('recipe_id')

    db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).filter_by(meal='lunch').update(dict(active_ind=False), synchronize_session=False)

    db.session.flush()
    db.session.commit()

    return render_template('meal_planning/meal_plan.html')


# Define route for manually removing DINNER recipe from meal plan
@bp.route('/_remove_dinner_meal_plan', methods=['GET', 'POST'])
@login_required
def _remove_dinner_meal_plan():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    recipe_id = request.form.get('recipe_id')

    db.session.query(Current_Meal).filter_by(recipe_id=recipe_id).filter_by(combined_user_id=combined_user_id).filter_by(active_ind=True).filter_by(meal='dinner').update(dict(active_ind=False), synchronize_session=False)

    db.session.flush()
    db.session.commit()

    return render_template('meal_planning/meal_plan.html')


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

        favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe).join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id).filter(Favorite_Recipe.app_user_id==current_user.id).filter(Recipe.recipe_deleted==False)).order_by(Recipe.recipe_name).all()

        fav_length = len(favorite_recipe_list)

        if fav_length != 0:
            fav_exists = True
        else:
            fav_exists = False 

    # If user selected to remove recipe from favorites, update table
    elif status == 'unchecked':
        db.session.query(Favorite_Recipe).filter(Favorite_Recipe.app_user_id==current_user.id).filter(Favorite_Recipe.recipe_id==recipe_id).delete(synchronize_session="fetch")

        db.session.flush()
        db.session.commit()

        favorite_recipe_list = (db.session.query(Recipe, Favorite_Recipe).join(Favorite_Recipe, Recipe.recipe_id==Favorite_Recipe.recipe_id).filter(Favorite_Recipe.app_user_id==current_user.id).filter(Recipe.recipe_deleted==False)).order_by(Recipe.recipe_name).all()

        fav_length = len(favorite_recipe_list)

        if fav_length != 0:
            fav_exists = True
        else:
            fav_exists = False 

    return render_template('view_recipes/recipe_list_favorites.html', favorite_recipe_list=favorite_recipe_list, fav_length=fav_length, fav_exists=fav_exists)


# Define route for deleting shopping list items
@bp.route('/_del_shopping_list_items', methods=['GET', 'POST'])
@login_required
def _del_shopping_list_items():

    # Get combined_user_id
    combined_user_id = (db.session.query(User_Link.combined_user_id).filter(User_Link.app_user_id==current_user.id))

    s_list_id = request.form.get('s_list_id')

    # Delete value from database
    Shopping_List.query.filter_by(shopping_list_id=s_list_id).delete(synchronize_session="fetch")

    db.session.flush()
    db.session.commit()

    # Query for shopping list items
    shop_list = (db.session.query(
        Shopping_List, 
        Recipe
    ).join(
        Recipe, Recipe.recipe_id==Shopping_List.recipe_id
    ).filter(
        Shopping_List.combined_user_id==combined_user_id
    ).order_by(Shopping_List.item_sort).all())

    return render_template('meal_planning/shopping_list.html', shop_list=shop_list)


   