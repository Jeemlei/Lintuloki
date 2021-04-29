from app import app
from db import db
from flask import session, abort
from datetime import timedelta
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
import traceback


app.secret_key = getenv("SECRET_KEY")


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)


def logged_in(checkAdmin):
    admin = False
    username = ''
    try:
        print('Checking login status...')
        user_id = session['user_id']
        username = session['username']
        if checkAdmin:
            print('Checking admin privileges...')
            sql = 'SELECT admin_status \
                    FROM users \
                    WHERE id=:id \
                        AND username=:username'
            admin = db.session.execute(
                sql, {'id': user_id, 'username': username}).fetchone()['admin_status']
        else:
            print(username, 'authorized!')
            return True
    except Exception as e:
        print('Authorization error:', e)
        return False

    if not admin:
        abort(403)
    else:
        print('Admin priviliges confirmed for', username)
        return True


def authorized_obs(obsid):
    username = ''
    try:
        print('Checking authorization...')
        sql = 'SELECT u.id, u.username \
                FROM observations o \
                INNER JOIN users u ON u.id=o.user_id \
                WHERE o.id=:obsid'
        user = db.session.execute(sql, {'obsid': obsid}).fetchone()
        username = user['username']

        if not session['username'] == username or not session['user_id'] == user['id']:
            abort(403)

    except Exception as e:
        print('Authorization error: User is not the owner of this log ::', e)
        if not logged_in(True):
            abort(403)

    print(username, 'authorized!')
    return True


def authorized_comment(comment_id):
    username = ''
    try:
        print('Checking authorization...')
        sql = 'SELECT u.id, u.username, o.user_id AS owner \
                FROM comments c \
                INNER JOIN users u ON u.id=c.user_id \
                INNER JOIN observations o ON o.id=c.observation_id \
                WHERE c.id=:id'
        user_and_owner = db.session.execute(sql, {'id': comment_id}).fetchone()
        username = user_and_owner['username']

        if (not session['username'] == username or not session['user_id'] == user_and_owner['id']) and not session['user_id'] == user_and_owner['owner']:
            abort(403)

    except Exception as e:
        print('Authorization error: User is not the owner of this comment ::', e)
        if not logged_in(True):
            abort(403)

    print(username, 'authorized!')
    return True


def new_user(name, username, password):
    if len(password) < 8:
        return False

    psswrdhash = generate_password_hash(password)

    try:
        sql = 'INSERT INTO users (realname, username, psswrdhash) VALUES (:name, :username, :psswrdhash)'
        db.session.execute(
            sql, {'name': name, 'username': username, 'psswrdhash': psswrdhash})
        db.session.commit()
    except Exception as e:
        print('Exception:', e)
        traceback.print_exc()
        return False

    return True


def start_session(username, password):
    sql = 'SELECT id, psswrdhash, admin_status FROM Users WHERE username=:username'
    result = db.session.execute(sql, {'username': username})
    user = result.fetchone()

    if user and check_password_hash(user['psswrdhash'], password):
        session['user_id'] = user['id']
        session['username'] = username
        session['admin_status'] = user['admin_status']
        return True

    return False


def end_session():
    try:
        del session['user_id']
        del session['username']
        del session['admin_status']
    except Exception as e:
        print('Exception:', e)
        traceback.print_exc()
