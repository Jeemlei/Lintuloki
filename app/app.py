from os import getenv
from flask import Flask, render_template, redirect, request, session, abort, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)

import routes
import errors
