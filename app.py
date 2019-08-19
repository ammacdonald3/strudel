from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}! Welcome to the site".format(name)

if __name__ == '__main__':
    app.run()