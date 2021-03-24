from os import getenv
from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html', title='Lintubongarin lokisovellus')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        psswrdhash = generate_password_hash(password)

        try:
            sql = 'INSERT INTO Users (realname, username, psswrdhash) VALUES (:name, :username, :psswrdhash)'
            db.session.execute(sql, {'name':name,'username':username,'psswrdhash':psswrdhash})
            db.session.commit()
        except Exception as e:
            print(e)
            return redirect('/register')

        return redirect('/')
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        sql = 'SELECT psswrdhash FROM users WHERE username=:username'
        result = db.session.execute(sql, {'username':username})
        user = result.fetchone()

        if user:
            session['username'] = username
            return redirect('/')
        else:
            redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')