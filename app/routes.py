from app import app
from flask import render_template, redirect, request, make_response
from auth import logged_in, authorized_obs, authorized_comment, new_user, start_session, end_session
from observations import create_observation, create_image, create_comment, update_observation, delete_observation, delete_comment, delete_all_comments, delete_image, get_birds, get_locations, get_observations, get_observation, get_image, get_comments
from datetime import datetime


@app.route('/')
def index():
    return render_template('index.html', title='Lintuloki')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if logged_in(False):
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
    if logged_in(False):
        return redirect('/')

    if request.method == 'POST':
        # -- REQUEST VALUES --
        # username  : string
        # password  : string
        if start_session(request.form['username'], request.form['password']):
            return redirect('/observations/page/1')

        return redirect('/login')

    # ----- GET /login -----
    return render_template('login.html', title='Kirjaudu')


@app.route('/logout')
def logout():
    end_session()
    return redirect('/')


@app.route('/new-observation', methods=['GET', 'POST'])
def new_observation():
    if not logged_in(False):
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

        if request.files['uploadImage']:
            create_image(observation_id, request.files)

        return redirect(f'/observations/{observation_id}')

    # ----- GET /new-observation -----
    birds = get_birds()
    locations = get_locations()

    return render_template('new_observation.html', title='Uusi havainto', birdpattern=birds[1], birds=birds[0],
                           locationpattern=locations[1], locations=locations[0], today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/images/<int:id>')
def image(id):
    image = get_image(id)
    # image = [(<binarydata>, 'imagename')]
    response = make_response(bytes(image[0][0]))
    imagetype = image[0][1].rsplit('.', 1)[1].lower()
    response.headers.set('Content-Type', f'image/{imagetype}')
    response.headers.set('Content-Disposition', f'inline; filename="{image[0][1]}"')
    return response


@app.route('/observations')
def resetSearch():
    resp = make_response(redirect('/observations/page/1'))
    resp.set_cookie('search',
                    f'all;;2021-01-01;{datetime.now().strftime("%Y-%m-%d")}')
    return resp


@app.route('/observations/page/<int:page>', methods=['GET', 'POST'])
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


@app.route('/observations/<int:id>')
def observation(id):
    observation = get_observation(id)
    observation['date'] = observation['date'].strftime('%-d.%-m.%Y')
    return render_template('observation.html', title='Lintuloki - Havainto', observation=observation, comments=get_comments(id))


@app.route('/comment/<int:obsid>', methods=['POST'])
def comment(obsid):
    if not logged_in(False):
        return redirect('/login')

    # -- REQUEST VALUES --
    # comment : string
    create_comment(obsid, request.form['comment'])
    return redirect(f'/observations/{obsid}')


@app.route('/edit/<int:obsid>', methods=['GET', 'POST'])
def edit(obsid):
    if not authorized_obs(obsid):
        return redirect('/login')

    if request.method == 'POST':
        # -- REQUEST VALUES --
        # deleteImg     : text          ("true"/"false")
        # uploadImage   : file/empty    (.apng/.avif/.gif/.jpg/.jpeg/.jfif/.pjpeg/.pjp/.png/.svg/.webp)
        # date          : date
        # location 	    : text
        # count         : number        (1-1000)
        # (band-serial  : text)
        if request.form['deleteImg'] == 'true':
            delete_image(obsid)

        if request.files['uploadImage']:
            delete_image(obsid)
            create_image(obsid, request.files)

        update_observation(obsid, request.form)

        return redirect(f'/observations/{obsid}')

    observation = get_observation(obsid)
    observation['date'] = observation['date'].strftime('%Y-%m-%d')

    locations = get_locations()

    return render_template('edit.html', title='Lintuloki - Muokkaa', observation=observation, locationpattern=locations[1], locations=locations[0], comments=get_comments(obsid), today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/observations/delete', methods=['POST'])
def delete_o():
    obsid = request.form['obsid']
    if authorized_obs(obsid):
        delete_observation(obsid)
    return redirect('/observations/page/1')


@app.route('/comments/delete', methods=['POST'])
def delete_c():
    comment_id = request.form['comment']
    if authorized_comment(comment_id):
        delete_comment(comment_id)
    return redirect(f'/observations/{request.form["obsid"]}')