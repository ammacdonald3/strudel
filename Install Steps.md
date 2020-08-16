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
        * ```export FLASK_APP="app.py"```
        * ```export APP_SETTINGS="config.DevelopmentConfig"```
        * ```export DATABASE_URL="postgresql:///recipe-dev"```
    * WINDOWS
        * ```$env:FLASK_APP="app.py"```
        * ```$env:APP_SETTINGS="config.DevelopmentConfig"```
        * ```$env:DATABASE_URL="postgresql:///recipe-dev"```
8. Navigate to root directory of project
9. Create data model in database
    * ```python manage.py db init```
    * ```python manage.py db migrate```
    * ```python manage.py db upgrade```
10. Run flask app
    * MAC OS: ```flask run```
    * WINDOWS: ```python -m flask run```


