# Extra app.py code:

# AJAX
#rendering the HTML page which has the button
@app.route('/json')
def json():
    return render_template('json.html')

#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    print("Hello")
    return "nothing"


# Define route so that user can favorite a recipe
@app.route('/favorite_recipe_route', methods=['GET', 'POST'])
@login_required
def favorite():
    output=[]
    #recipe_id = request.args.get('recipe_id', default=2)
    #recipe_id = jsonify(request.form.get('recipe_id'))
    #recipe_id = request.form['recipe_id']
    #recipe_id = request.args['recipe_id']
    recipe_id = request.get_json()
    #recipe_id = request.get_data()
    print("ANDREW ANDREW ANDREW")
    print(recipe_id)
    #print(request.args['recipe_id'])

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

            
    except Exception as e:
        db.session.rollback()
        output.append("Application encountered an error, and the recipe didn't write to the database. Better luck in the future!")
        output.append(str(e))
        print(output)

    return str(recipe_id)