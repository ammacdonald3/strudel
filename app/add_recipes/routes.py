from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort, send_from_directory, current_app
import flask_sqlalchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from recipe_scrapers import scrape_me
from datetime import datetime
from uuid import uuid4
from sqlalchemy import or_, func
import re
import os
from google.oauth2 import id_token
from google.auth.transport import requests

from app.add_recipes.upload_image import upload_file
from app.add_recipes.clean_url import clean
from app.add_recipes.validate_image import validate_image

from flask import current_app as app

from app import db

from app.models import Recipe, Ingredient, Recipe_Step, App_User, Current_Meal, User_Recipe, Favorite_Recipe, App_Error

from app.add_recipes import bp


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
                insert_datetime=datetime.now(),
                recipe_deleted=False,
                editor_certified=False
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
        # return(render_template('add_recipes/recipe_confirm.html', recipe_id=recipe.recipe_id, recipe_name=request.form['recipe_name']))
        return redirect(url_for('view_recipes.recipe_detail', recipe_id=recipe_id))

    # When not posting form, render the add.html template (main page for this route)
    #return render_template('add.html', output=output)
    return render_template('add_recipes/add.html')



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

                # BELOW LINES USED FOR TROUBLESHOOTING IMPORT ISSUES
                error = 'Recipe scraping error'

                return render_template("add_recipes/auto_import.html", error=error)

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
                    insert_datetime=datetime.now(),
                    recipe_deleted=False,
                    editor_certified=False
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

                # BELOW LINES USED FOR TROUBLESHOOTING IMPORT ISSUES
                error = 'Recipe initial insert error'

                return render_template("add_recipes/auto_import.html", error=error)


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

                    # BELOW LINES USED FOR TROUBLESHOOTING IMPORT ISSUES
                    error = 'Ingredients error'

                    return render_template("add_recipes/auto_import.html", error=error)

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
                    error = 'Recipe steps error'

                    return render_template("add_recipes/auto_import.html", error=error)


            # Insert data to FAVORITE_RECIPE table
            try:
                if 'mark_fav' in request.form:
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

                # BELOW LINES USED FOR TROUBLESHOOTING IMPORT ISSUES
                error = 'Favorite recipe error'

                return render_template("add_recipes/auto_import.html", error=error)


            # Render recipe_confirm.html template after recipe is written to DB
            # return(render_template('add_recipes/recipe_confirm.html', recipe_id=recipe.recipe_id, recipe_name=scraper.title(), output=output))
            return redirect(url_for('view_recipes.recipe_detail', recipe_id=recipe.recipe_id))
            
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

            return render_template("add_recipes/auto_import.html", error=error)

            

    # When not posting form, render the auto_import.html template (main page for this route)
    return render_template("add_recipes/auto_import.html", output=output)


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
        # Clean image input and upload to AWS S3
        try:
            uploaded_file = request.files['file']
            filename_sec = secure_filename(uploaded_file.filename)

            # print("--------------------FILENAME--------------------")
            # print(filename_sec)
            # print("--------------------FILENAME--------------------")

            if filename_sec != '':
                file_ext_base = os.path.splitext(filename_sec)[1]
                if file_ext_base == '.jpeg':
                    file_ext = '.jpg'
                else:
                    file_ext = file_ext_base

                # print("--------------------FILE EXT--------------------")
                # print(file_ext)
                # print("--------------------FILE EXT--------------------")

                if file_ext in current_app.config['UPLOAD_EXTENSIONS'] and \
                    file_ext == validate_image(uploaded_file.stream):

                        # Generate unique file name
                        filename = str(uuid4()) + file_ext

                        # print("--------------------FILENAME2--------------------")
                        # print(filename)
                        # print("--------------------FILENAME2--------------------")

                        # Call the upload_image.upload_file function to physically upload the image to AWS
                        image_url = upload_file(uploaded_file, current_app.config['BUCKET'], filename)

                        # print("--------------------IMAGE URL--------------------")
                        # print(image_url)
                        # print("--------------------IMAGE URL--------------------")

                        # Update database table with AWS URL for the image
                        db.session.query(Recipe).filter_by(recipe_id=recipe_id).update(dict(recipe_image_url=image_url))

                        db.session.flush()
                        db.session.commit()
                else:
                    error = "Invalid image upload. Images must be a maximum size of 1024x1024 and one of the following types: .JPG or .PNG"
                    print(error)
                    return render_template('errors/error.html', error=error)

            else:
                error = "Invalid image upload. Images must be a maximum size of 1024x1024 and one of the following types: .JPG or .PNG"
                print(error)
                return render_template('errors/error.html', error=error)
    

        except Exception as e:
            output.append("Application encountered an error, and the image was not uploaded. Better luck in the future!")
            output.append(str(e))
            print(str(e))
            return render_template('errors/error.html', error=e)

        # Render recipe_confirm.html template after image URL is written to DB    
        # return(render_template('add_recipes/recipe_confirm.html', recipe_id=recipe.recipe_id, recipe_name=recipe.recipe_name))
        return redirect(url_for('view_recipes.recipe_detail', recipe_id=recipe_id))


    # When not posting form, render the upload_image.html template (main page for this route)
    return render_template('add_recipes/upload_image.html', recipe=recipe)



# Define route for page to modify existing recipes
@bp.route('/edit/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    output = []
    recipe = db.session.query(Recipe).filter_by(recipe_id=recipe_id).join(App_User).first()

    ingredient_list = Ingredient.query.filter_by(recipe_id=recipe_id).order_by(Ingredient.ingredient_id)
    ingredient_count = ingredient_list.count()

    step_list = Recipe_Step.query.filter_by(recipe_id=recipe_id).order_by(Recipe_Step.recipe_step_id)
    step_count = step_list.count()


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

            # Determine number of ingredients currently on the form
            ing_count = int(request.form['ing_count']) + 1


            # Insert data to INGREDIENT table
            for x in range(1, ing_count):
                try:
                    # Check if ingredient contains letters
                    ing = request.form['ingredient_desc' + str(x)]

                    if ing.upper().isupper():
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

            # Determine number of steps currently on the form
            step_count = int(request.form['step_count']) + 1

            # Insert data to RECIPE_STEP table
            counter = 1
            for x in range(1, step_count):
                try:
                    # Check if step contains letters
                    step = request.form['recipe_step' + str(x)]
                    if step.upper().isupper():
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
            # return(render_template('add_recipes/recipe_confirm.html', recipe_id=recipe.recipe_id, error=error, recipe_name=request.form['recipe_name']))
            return redirect(url_for('view_recipes.recipe_detail', recipe_id=recipe_id))

        except Exception as e:
            return render_template('errors/error.html', error=e)

    # When not posting form, render the edit_recipe.html template (main page for this route)
    return render_template('add_recipes/edit_recipe.html', recipe=recipe, ingredient_list=ingredient_list, ingredient_count=ingredient_count, step_list=step_list, step_count=step_count)
