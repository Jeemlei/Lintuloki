from app import app
from flask import render_template


def bad_request(e):
    return render_template('error.html', title='ERROR404', header='400 ERROR', description='Pyynnössäsi oli jotain vikana...')


def forbidden(e):
    return render_template('error.html', title='ERROR404', header='403 ERROR', description='Sinulla ei ole oikeutta pyytämääsi toimintoon...')


def not_found(e):
    return render_template('error.html', title='ERROR404', header='404 ERROR', description='Etsimääsi resurssia ei löytynyt...')


def unsupported_media_type(e):
    return render_template('error.html', title='ERROR404', header='415 ERROR', description='Lähettämääsi mediatyyppiä ei tueta...')


def internal_server_error(e):
    return render_template('error.html', title='ERROR404', header='500 ERROR', description='Serverillä meni jotain pieleen...')


app.register_error_handler(400, bad_request)
app.register_error_handler(403, forbidden)
app.register_error_handler(404, not_found)
app.register_error_handler(415, unsupported_media_type)
app.register_error_handler(500, internal_server_error)
