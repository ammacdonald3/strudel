# Install Steps:

1. Clone repository
2. Create virtual environment outside of repo (```python3 -m venv recipe-venv```)
3. Activate virtual environment
    * MAC OS: 
        * ```cd Google_Drive/"Software Dev"/git```
        * ```source recipe-venv/bin/activate```
    * WINDOWS: ```recipe-venv\Scripts\Activate.ps1```
4. Install requirements.txt into virtual machine
    * MAC OS: ```pip install -r recipe-app/requirements.txt```
    * WINDOWS:
5. Install Postgres on local machine
5. Add Postgres bin directory to PATH envrionment variable
6. Create Postgres database
    * ```psql```
    * ```create database recipe_dev;```
    * ```\q```
7. Set environment variables
    * MAC OS
        * ```export FLASK_APP="strudel.py"```
        * ```export APP_SETTINGS="config.DevelopmentConfig"```
        * ```export DATABASE_URL="postgresql:///strudel-dev"```
        * ```export GOOGLE_LOGIN_URI="http://localhost:5000/auth/register"```
        * ```export GOOGLE_CLIENT_ID="<populate from Google>```
        * ```export SECRET_KEY="123"```
    * WINDOWS
        * ```$env:FLASK_APP="strudel.py"```
        * ```$env:APP_SETTINGS="config.DevelopmentConfig"```
        * ```$env:DATABASE_URL="postgresql:///recipe-dev"```
8. Navigate to root directory of project
9. Create data model in database
    * ```flask db init```
    * ```flask db migrate -m "Initial migration."```
    * ```flask db upgrade```
10. Run flask app
    * MAC OS: ```flask run --host=0.0.0.0```
    * WINDOWS: ```python -m flask run```
11. Update Heroku database
    * ``` heroku run flask db upgrade --app recipe-stage ```
    * ``` heroku run flask db upgrade --app recipe-prod ```
12. After each update
    * Commit changes in local git
    * Push committed changes to remote STAGE git branch
    * Check out MASTER branch
        * ``` git checkout master ```
    * Merge changes from STAGE branch into MASTER
        * ``` git merge stage ```
    * Push changes to remote MASTER
        * ``` git push origin master ```
    * Check out STAGE again for future development
        * ``` git checkout stage ```

13. After each update (temp deployment directly to Heroku)
    * Commit changes in local git
    * Push committed changes to remote STAGE git branch
    * Create remote for Stage app on Heroku
        * ``` heroku git:remote -a recipe-stage ```
    * Push changes to Heroku Stage
        * ``` git push heroku stage:main ```
    * Check out Master branch
    * Merge changes from STAGE branch into MASTER
    * Push changes to remote MASTER
    * Create remote for Stage app on Heroku
        * ``` heroku git:remote -a strudel-app ```
    * Push changes to Heroku Stage
        * ``` git push heroku master:main ```
    * Check out STAGE again for future development

