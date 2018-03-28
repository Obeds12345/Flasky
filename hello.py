from flask import Flask
app = Flask(__name__)


# @app.route('/')
# def index():
#     return '<h1>Hello World!</h1>'


@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s!</h1>' % name

from flask import make_response

# @app.route('/')
# def index():
#     response = make_response('<h1>This document carries a cookie!</h1>')
#     response.set_cookie('answer', '42')
#     return response

from flask import redirect

@app.route('/')
def index():
    return redirect('http://www.example.com')

if __name__ == '__main__':
    app.run(debug=True)
