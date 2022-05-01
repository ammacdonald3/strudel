import os
from app import create_app, db
from app.models import Recipe, Ingredient, Recipe_Step, App_User, Current_Meal, User_Recipe, Favorite_Recipe, Shopping_List, App_Error
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Recipe=Recipe, Recipe_Step=Recipe_Step, App_User=App_User, Current_Meal=Current_Meal, User_Recipe=User_Recipe, Favorite_Recipe=Favorite_Recipe, Shopping_List=Shopping_List, App_Error=App_Error)