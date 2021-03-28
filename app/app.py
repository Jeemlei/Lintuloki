from os import getenv
from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)

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
            return redirect('/new-observation')
        else:
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/new-observation', methods=['GET', 'POST'])
def new_observation():
    if request.method == 'POST':
        return redirect('/')

    result = db.session.execute('SELECT fi FROM birds')
    birdpattern = ''
    birds = []
    for b in result.fetchall():
        birdpattern += f'{b[0]}|'
        birds.append(b[0])
    birdpattern = birdpattern[:-1]

    result = db.session.execute('SELECT muni FROM locations')
    locationpattern = ''
    locations = []
    for l in result.fetchall():
        locationpattern += f'{l[0]}|'
        locations.append(l[0])
    locationpattern = locationpattern[:-1]

    today = datetime.now().strftime('%Y-%m-%d')

    return render_template('new_observation.html', birdpattern=birdpattern, birds=birds, locationpattern=locationpattern, locations=locations, today=today)
