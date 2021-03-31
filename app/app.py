from os import getenv
from flask import Flask, render_template, redirect, request, session, abort
from flask_sqlalchemy import SQLAlchemy  # pylint: disable=import-error
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import traceback

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)


def handle_not_found(e):
    return render_template('404.html', title='ERROR404')


app.register_error_handler(404, handle_not_found)


def authorized_user(admin):
    try:
        print('Checking login status...')
        user_id = session['user_id']
        username = session['username']
        if admin:
            print('Checking admin privileges...')
            admin = db.session.execute('SELECT admin_status FROM users WHERE id=:id AND username=:username', {
                                       'id': user_id, 'username': username})
            abort(403)
        print(username, 'authorized!')
        return True
    except Exception as e:
        print('Authorization error:', e)
        return False


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)


@app.route('/')
def index():
    return render_template('index.html', title='Lintuloki')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # -- REQUEST VALUES --
        # name      : string
        # username  : string
        # password  : string
        password = request.form['password']
        if len(password) < 8:
            return redirect('/register')
        name = request.form['name']
        username = request.form['username']
        psswrdhash = generate_password_hash(password)

        try:
            sql = 'INSERT INTO users (realname, username, psswrdhash) VALUES (:name, :username, :psswrdhash)'
            db.session.execute(
                sql, {'name': name, 'username': username, 'psswrdhash': psswrdhash})
            db.session.commit()
        except Exception as e:
            print('Exception:', e)
            traceback.print_exc()
            return redirect('/register')

        return redirect('/login')

    # ----- GET /register -----
    return render_template('register.html', title='Rekisteröidy')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if authorized_user(False):
        return redirect('/')

    if request.method == 'POST':
        # -- REQUEST VALUES --
        # username  : string
        # password  : string
        username = request.form['username']
        password = request.form['password']

        sql = 'SELECT id, psswrdhash FROM Users WHERE username=:username'
        result = db.session.execute(sql, {'username': username})
        user = result.fetchone()

        if user and check_password_hash(user['psswrdhash'], password):
            session['user_id'] = user['id']
            session['username'] = username
            return redirect('/new-observation')
        else:
            return redirect('/login')

    # ----- GET /login -----
    return render_template('login.html', title='Kirjaudu')


@app.route('/logout')
def logout():
    try:
        del session['user_id']
        del session['username']
    except Exception as e:
        print('Exception:', e)
        traceback.print_exc()
    return redirect('/')


@app.route('/new-observation', methods=['GET', 'POST'])
def new_observation():
    if not authorized_user(False):
        return redirect('/login')

    if request.method == 'POST':
        # -- REQUEST VALUES --
        # bird          : string
        # location      : string
        # date          : string        (yyyy-mm-dd)
        # count-option  : string        ('one'/'many')
        # count         : string/None
        # banded-option : string        ('true'/'false'/'not_known')
        # band-serial   : string/None
        # uploadImage   : file/None     (.apng/.avif/.gif/.jpg/.jpeg/.jfif/.pjpeg/.pjp/.png/.svg/.webp)
        bird = request.form['bird']
        location = request.form['location']
        date = request.form['date']
        count_option = request.form['count-option']

        observation_id = None

        try:
            location_id = db.session.execute('SELECT id FROM locations WHERE muni=:location', {
                                             'location': location}).fetchone()['id']
            bird_id = db.session.execute('SELECT id FROM birds WHERE fi=:bird', {
                                         'bird': bird}).fetchone()['id']

            # ----- SAVE OBSERVATION -----
            sql = "INSERT INTO Observations (user_id, location_id, bird_id, observation_date, bird_count, banded, band_serial) \
                    VALUES (:user_id, :location_id, :bird_id, TO_DATE(:observation_date, 'YYYY-MM-DD'), :count, :banded, :band_serial) \
                    RETURNING id"

            if count_option == 'one':
                banded_option = request.form['banded-option']

                if banded_option == 'true':
                    band_serial = request.form['band-serial']
                    observation_id = db.session.execute(sql, {'user_id': session['user_id'], 'location_id': location_id, 'bird_id': bird_id,
                                                        'observation_date': date, 'count': 1, 'banded': banded_option, 'band_serial': band_serial}).fetchone()[0]

                elif banded_option == 'false' or banded_option == 'not_known':
                    observation_id = db.session.execute(sql, {'user_id': session['user_id'], 'location_id': location_id, 'bird_id': bird_id,
                                                        'observation_date': date, 'count': 1, 'banded': banded_option, 'band_serial': None}).fetchone()[0]

            elif count_option == 'many':
                count = request.form['count']
                observation_id = db.session.execute(sql, {'user_id': session['user_id'], 'location_id': location_id, 'bird_id': bird_id,
                                                    'observation_date': date, 'count': count, 'banded': 'not_known', 'band_serial': None}).fetchone()[0]

            db.session.commit()

        except Exception as e:
            print('Exception:', e)
            traceback.print_exc()
            return redirect('/new-observation')

        # ----- VALIDATE AND SAVE IMAGE -----
        try:
            image = request.files['uploadImage']
            imagename = image.filename
            allowedFiles = ('.apng', '.avif', '.gif', '.jpg', '.jpeg',
                            '.jfif', '.pjpeg', '.pjp', '.png', '.svg', '.webp')
            if observation_id and imagename.lower().endswith(allowedFiles):
                imagedata = image.read()
                sql = 'INSERT INTO images (observation_id, user_id, imagename, binarydata) VALUES (:observation_id, :user_id, :imagename, :data)'
                db.session.execute(sql, {'observation_id': observation_id, 'user_id': session['user_id'], 'imagename': secure_filename(
                    imagename), 'data': imagedata})
                db.session.commit()

        except Exception as e:
            print('Exception:', e)
            traceback.print_exc()

        return redirect('/')

    # ----- GET /new-observation -----
    result = db.session.execute('SELECT fi FROM birds ORDER BY fi')
    birdpattern = ''
    birds = []
    for b in result.fetchall():
        birdpattern += f'{b[0]}|'
        birds.append(b[0])
    birdpattern = birdpattern[:-1]

    result = db.session.execute('SELECT muni FROM locations ORDER BY muni')
    locationpattern = ''
    locations = []
    for l in result.fetchall():
        locationpattern += f'{l[0]}|'
        locations.append(l[0])
    locationpattern = locationpattern[:-1]

    today = datetime.now().strftime('%Y-%m-%d')

    return render_template('new_observation.html', title='Uusi havainto', birdpattern=birdpattern, birds=birds, locationpattern=locationpattern, locations=locations, today=today)
