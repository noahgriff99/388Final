# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from flask_mail import Mail

# stdlib
from datetime import datetime
import os

# local
from .client import MovieClient

mail = Mail()
db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
movie_client = MovieClient(os.environ.get("OMDB_API_KEY"))

# from .routes import main

from flask_app.users.routes import users
from flask_app.movies.routes import movies



def page_not_found(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PASSWORD'] = 'Hpraza9oSx8Xbi'
    app.config['MAIL_USERNAME'] = '388jfinal@gmail.com' 
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_PORT'] = 587
    mail.init_app(app)

    app.register_blueprint(movies)
    app.register_blueprint(users)

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # app.register_blueprint(main)
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app
