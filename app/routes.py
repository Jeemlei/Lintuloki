from app import app
from flask import render_template, redirect, request, session, abort, make_response
from auth import authorized_user, new_user, start_session, end_session
from observations import create_observation, create_image, get_birds, get_locations, get_observations, get_image
from datetime import datetime


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
        if new_user(request.form['name'], request.form['username'], request.form['password']):
            return redirect('/login')

        return redirect('/register')

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
        if start_session(request.form['username'], request.form['password']):
            return redirect('/new-observation')

        return redirect('/login')

    # ----- GET /login -----
    return render_template('login.html', title='Kirjaudu')


@app.route('/logout')
def logout():
    end_session()
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
        observation_id = create_observation(request.form)

        if not observation_id:
            return redirect('/new-observation')

        create_image(observation_id, request.files)

        return redirect('/observations')

    # ----- GET /new-observation -----
    birds = get_birds()
    locations = get_locations()

    return render_template('new_observation.html', title='Uusi havainto', birdpattern=birds[1], birds=birds[0],
                           locationpattern=locations[1], locations=locations[0], today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/observations')
def resetSearch():
    resp = make_response(redirect('/observations/1'))
    resp.set_cookie('search',
                    f'all;;2021-01-01;{datetime.now().strftime("%Y-%m-%d")}')
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
    observations = get_observations(
        criterion, keyword, start_date, end_date, page, pagesize)

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
    image = get_image(id)
    # image = [(<binarydata>, 'imagename')]
    response = make_response(bytes(image[0][0]))
    imagetype = image[0][1].rsplit('.', 1)[1].lower()
    response.headers.set('Content-Type', f'image/{imagetype}')
    return response
