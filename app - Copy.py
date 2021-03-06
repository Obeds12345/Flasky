from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from data import Articles
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import psycopg2
import psycopg2.extras
import sys

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False                 
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:obeds@localhost/My_DB'
app.config['SQLALCHEMY_CURSORCLASS'] = 'DictCursor'



db = SQLAlchemy(app)

class users(db.Model):
    name = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    username = db.Column(db.String(50))
    password = db.Column(db.String(80))
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


        # Create cursor
        
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s, %s)", (name, email, username, password, admin))

        # Commit to DB
        conn.commit()

        # Close connection
        cur.close()

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

        # Create cursor
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if 1 > 0:
            # Get stored hash
            data = cur.fetchone()
           #print (result)
            #print (data)
            #sys.exit()
            password = data[3]

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                #session['logged_in'] = True
                #session['username'] = username
                app.logger.info('Password matched')

                #flash('You are now logged in', 'success')
                #return redirect(url_for('dashboard'))
            else:
                app.logger.info('Password Dont matched')
                #error = 'Invalid login'
                #return render_template('login.html', error=error)
            # Close connection
            #cur.close()
        else:
            app.logger.info('No user')
            #error = 'Username not found'
            #return render_template('login.html', error=error)

    return render_template('login.html')


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)