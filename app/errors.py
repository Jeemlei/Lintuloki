from app import app
from flask import render_template


def not_found(e):
    return render_template('404.html', title='ERROR404')


#app.register_error_handler(400, bad_request)
#app.register_error_handler(403, forbidden)
#app.register_error_handler(415, unsupported_media_type)
app.register_error_handler(404, not_found)
#app.register_error_handler(500, internal_server_error)
