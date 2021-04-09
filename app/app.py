from os import getenv
from flask import Flask, render_template, redirect, request, session, abort, make_response
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


def authorized_user(checkAdmin):
    try:
        print('Checking login status...')
        user_id = session['user_id']
        username = session['username']
        if checkAdmin:
            print('Checking admin privileges...')
            admin = db.session.execute('SELECT admin_status FROM users WHERE id=:id AND username=:username', {
                                       'id': user_id, 'username': username}).fetchone()['admin_status']
            if not admin:
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
    if authorized_user(False):
        return redirect('/')

    if request.method == 'POST':
        # -- REQUEST VALUES --
        # name              : string
        # username          : string
        # password          : string
        # password_confirm  : string
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

        return redirect('/observations')

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

    return render_template('new_observation.html', title='Uusi havainto', birdpattern=birdpattern, birds=birds,
                           locationpattern=locationpattern, locations=locations, today=today)


@app.route('/observations')
def resetSearch():
    resp = make_response(redirect('/observations/1'))
    resp.set_cookie('search', f'all;;2021-01-01;{datetime.now().strftime("%Y-%m-%d")}')
    return resp


@app.route('/observations/<int:page>', methods=['GET', 'POST'])
def observations(page):
    # -- POSSIBLE SEARCH VALUES --
    # criterion	: string		("all"/"bird"/"location"/"band"/"observer")
    # keyword	: string/None
    # from		: string        (yyyy-mm-dd)
    # to		: string        (yyyy-mm-dd)
    criterion = 'all'
    keyword = ''
    start_date = '2021-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')

    try:
        criterion = request.form['criterion']
        try:
            keyword = request.form['keyword']
        except:
            print('No keyword')
        start_date = request.form['from']
        end_date = request.form['to']
    except:
        searchCookie = request.cookies.get('search')
        if searchCookie:
            searchCookie = searchCookie.split(';')
            criterion = searchCookie[0]
            keyword = searchCookie[1]
            start_date = searchCookie[2]
            end_date = searchCookie[3]

    pagesize = 5

    params = {'bird': '%', 'location': '%', 'observer': '%',
              'start_date': start_date, 'end_date': end_date}
    sql = 'SELECT b.fi, b.sci, o.observation_date AS date, l.muni, l.prov, o.bird_count, u.realname, i.id AS imgid \
            FROM observations o \
            INNER JOIN users u ON o.user_id=u.id \
            INNER JOIN locations l ON o.location_id=l.id \
            INNER JOIN birds b ON o.bird_id=b.id \
            LEFT JOIN images i ON o.id=i.observation_id \
            WHERE b.fi ILIKE :bird \
                AND (l.muni ILIKE :location OR l.prov ILIKE :location) '
    if criterion == 'band':
        sql += 'AND o.band_serial ILIKE :band_serial'
        params['band_serial'] = f'%{keyword}%'
    sql += f"   AND (u.realname ILIKE :observer OR u.username ILIKE :observer) \
                AND o.observation_date>=TO_DATE(:start_date, 'YYYY-MM-DD') \
                AND o.observation_date<=TO_DATE(:end_date, 'YYYY-MM-DD') \
            ORDER BY date DESC \
            LIMIT {pagesize} OFFSET {pagesize * (page - 1)}"

    if criterion == 'bird':
        params['bird'] = f'%{keyword}%'
    elif criterion == 'location':
        params['location'] = f'%{keyword}%'
    elif criterion == 'observer':
        params['observer'] = f'%{keyword}%'

    result = db.session.execute(sql, params).fetchall()
    observations = []
    for o in result:
        observations.append({'birdfi': o[0], 'birdsci': o[1], 'date': o[2].strftime('%-d.%-m.%Y'), 'muni': o[3],
                             'prov': o[4], 'count': o[5], 'user': o[6], 'imgid': o[7]})

    pageinfo = {'pagenumber': page}
    if page > 1:
        pageinfo['previouspage'] = page - 1
    if len(observations) == pagesize:
        pageinfo['nextpage'] = page + 1
    form_content = {'criterion': criterion, 'keyword': keyword, 'start_date': start_date,
                    'end_date': end_date, 'today': datetime.now().strftime('%Y-%m-%d')}

    resp = make_response(render_template('observations.html', title='Lintuloki - Havainnot', observations=observations,
                                         pageinfo=pageinfo, lastpage=(len(observations) < 5), form_content=form_content))
    resp.set_cookie('search', f'{criterion};{keyword};{start_date};{end_date}')
    return resp


@app.route('/images/<int:id>')
def image(id):
    sql = 'SELECT binarydata, imagename FROM images WHERE id=:id'
    # result = [(<binarydata>, 'imagename')]
    result = db.session.execute(sql, {'id': id}).fetchall()
    response = make_response(bytes(result[0][0]))
    imagetype = result[0][1].rsplit('.', 1)[1].lower()
    response.headers.set('Content-Type', f'image/{imagetype}')
    return response
