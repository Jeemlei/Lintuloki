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
    sql = 'SELECT id, psswrdhash FROM Users WHERE username=:username'
    result = db.session.execute(sql, {'username': username})
    user = result.fetchone()

    if user and check_password_hash(user['psswrdhash'], password):
        session['user_id'] = user['id']
        session['username'] = username
        return True

    return False


def end_session():
    try:
        del session['user_id']
        del session['username']
    except Exception as e:
        print('Exception:', e)
        traceback.print_exc()
