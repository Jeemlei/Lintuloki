from db import db
from flask import session, abort
from werkzeug.utils import secure_filename
import traceback


def create_observation(request_form):
    observation_id = None

    try:
        location_id = db.session.execute('SELECT id FROM locations WHERE muni=:location', {
                                         'location': request_form['location']}).fetchone()['id']
        bird_id = db.session.execute('SELECT id FROM birds WHERE fi=:bird', {
                                     'bird': request_form['bird']}).fetchone()['id']

        sql = "INSERT INTO Observations (user_id, location_id, bird_id, observation_date, bird_count, banded, band_serial) \
                VALUES (:user_id, :location_id, :bird_id, TO_DATE(:observation_date, 'YYYY-MM-DD'), :count, :banded, :band_serial) \
                RETURNING id"

        if request_form['count-option'] == 'one':
            banded_option = request_form['banded-option']

            if banded_option == 'true':
                band_serial = request_form['band-serial']
                observation_id = db.session.execute(sql, {'user_id': session['user_id'], 'location_id': location_id, 'bird_id': bird_id,
                                                          'observation_date': request_form['date'], 'count': 1, 'banded': banded_option,
                                                          'band_serial': band_serial}).fetchone()[0]

            elif banded_option == 'false' or banded_option == 'not_known':
                observation_id = db.session.execute(sql, {'user_id': session['user_id'], 'location_id': location_id, 'bird_id': bird_id,
                                                          'observation_date': request_form['date'], 'count': 1, 'banded': banded_option,
                                                          'band_serial': None}).fetchone()[0]

        elif request_form['count-option'] == 'many':
            count = request_form['count']
            if count < 2 or 1000 < count:
                abort(400)
            observation_id = db.session.execute(sql, {'user_id': session['user_id'], 'location_id': location_id, 'bird_id': bird_id,
                                                      'observation_date': request_form['date'], 'count': count, 'banded': 'not_known',
                                                      'band_serial': None}).fetchone()[0]

        db.session.commit()

    except Exception as e:
        print('Exception:', e)
        traceback.print_exc()

    return observation_id


def create_image(observation_id, form_files):
    try:
        image = form_files['uploadImage']
        imagename = image.filename
        allowedFiles = ('.apng', '.avif', '.gif', '.jpg', '.jpeg',
                        '.jfif', '.pjpeg', '.pjp', '.png', '.svg', '.webp')
        if imagename.lower().endswith(allowedFiles):
            imagedata = image.read()
            sql = 'INSERT INTO images (observation_id, user_id, imagename, binarydata) \
                    VALUES (:observation_id, :user_id, :imagename, :data)'
            db.session.execute(sql, {'observation_id': observation_id, 'user_id': session['user_id'],
                                     'imagename': secure_filename(imagename), 'data': imagedata})
            db.session.commit()
        else:
            abort(415)

    except Exception as e:
        print('Exception:', e)
        traceback.print_exc()


def get_birds():
    result = db.session.execute('SELECT fi FROM birds ORDER BY fi')
    birdpattern = ''
    birds = []
    for b in result.fetchall():
        birdpattern += f'{b[0]}|'
        birds.append(b[0])
    return [birds, birdpattern[:-1]]


def get_locations():
    result = db.session.execute('SELECT muni FROM locations ORDER BY muni')
    locationpattern = ''
    locations = []
    for l in result.fetchall():
        locationpattern += f'{l[0]}|'
        locations.append(l[0])
    return [locations, locationpattern[:-1]]


def get_observations(criterion, keyword, start_date, end_date, page, pagesize):
    params = {'bird': '%', 'location': '%', 'observer': '%',
              'start_date': start_date, 'end_date': end_date}

    sql = 'SELECT b.fi, b.sci, o.observation_date AS date, l.muni, l.prov, o.bird_count, u.realname, i.id, o.id AS obsid \
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
            ORDER BY date DESC, obsid DESC \
            LIMIT {pagesize} OFFSET {pagesize * (page - 1)}"

    if criterion == 'bird':
        params['bird'] = f'%{keyword}%'

    if criterion == 'location':
        params['location'] = f'%{keyword}%'

    if criterion == 'observer':
        params['observer'] = f'%{keyword}%'

    result = db.session.execute(sql, params).fetchall()
    observations = []
    for o in result:
        observations.append({'birdfi': o[0], 'birdsci': o[1], 'date': o[2].strftime('%-d.%-m.%Y'), 'muni': o[3],
                             'prov': o[4], 'count': o[5], 'user': o[6], 'imgid': o[7]})

    return observations


def get_image(id):
    sql = 'SELECT binarydata, imagename FROM images WHERE id=:id'
    return db.session.execute(sql, {'id': id}).fetchall()
