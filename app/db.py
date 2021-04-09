from app import app
from flask_sqlalchemy import SQLAlchemy  # pylint: disable=import-error
from os import getenv

app.config["SQLALCHEMY_DATABASE_URI"] = getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)
