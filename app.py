from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from data import Articles
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, BooleanField ,validators
from passlib.hash import sha256_crypt
import psycopg2
import psycopg2.extras
import sys
from functools import wraps

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False                 
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:obeds@localhost/postgres'
app.config['SQLALCHEMY_CURSORCLASS'] = 'DictCursor'



db = SQLAlchemy(app)

class users(db.Model):
    name = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    username = db.Column(db.String(50))
    password = db.Column(db.String(200))
    admin = db.Column(db.Boolean)


Articles=Articles()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('comfirm', message='Passwords do not match')
    ])
    comfirm = PasswordField('Comfirm Password')
    admin=BooleanField('Admin', default=False)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        admin = form.admin.data

        new_user = users(name=name, email=email, username=username, password=password, admin=admin)
        db.session.add(new_user)
        db.session.commit()


        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # query user
        user = users.query.filter_by(username=username).first()
        if not user:
            error = 'No User found'
            return render_template('login.html', error=error)
        # Get user by username
        else:
            if 1 > 0:
                password = user.password
                # Compare Passwords
                if sha256_crypt.verify(password_candidate, password):
                    #Passed
                    session['logged_in'] = True
                    session['username'] = username

                    flash('You are now logged in', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error = 'Invalid login'
                    return render_template('login.html', error=error)
            else:
                error = 'Username not found'
                return render_template('login.html', error=error)

    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)