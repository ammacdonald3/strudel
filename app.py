from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/<string:name>')
def hello_name(name):
    name = name.capitalize()
    return f"Hello, {name}! Welcome to the site."

@app.route('/all')
def all():
    recipes = ['Steak','Chicken','Veal']
    return render_template('all.html', recipes=recipes)


if __name__ == '__main__':
    app.run()