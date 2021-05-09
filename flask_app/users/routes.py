from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user

from flask_pymongo import PyMongo
from flask_mail import Message

from .. import bcrypt, db, mail
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, LocationForm, SurveyForm
from ..models import User, Location, Survey

users = Blueprint('users', __name__)


@users.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    result = Location.objects(address=query)


    return result

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("movies.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        user.save()

        # msg = Message("Hello", sender="388jfinal@gmail.com", recipients=[form.email.data])
        # mail.send(msg)
        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("movies.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            msg = Message("Hello, nice email", sender="388jfinal@gmail.com", recipients=[user.email])
            mail.send(msg)
            return redirect(url_for("users.account"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("movies.index"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    username_form = UpdateUsernameForm()

    if username_form.validate_on_submit():
        # current_user.username = username_form.username.data
        current_user.modify(username=username_form.username.data)
        current_user.save()
        return redirect(url_for("users.account"))

    return render_template(
        "account.html",
        title="Account",
        username_form=username_form,
    )

# @users.route("/add", methods=["GET", "POST"])
# @login_required
# def add():
#     # username_form = UpdateUsernameForm()

#     form = LocationForm()

#     if form.validate_on_submit():
#         # User(username=form.username.data, email=form.email.data, password=hashed)
#         location = Location(address=form.address.data, state=form.state.data, zipcode=form.zipcode.data)
#         location.save()
#         return redirect(url_for("users.survey"))

#     return render_template("add.html", location_form = form)

# @users.route("/survey", methods=["GET", "POST"])
# @login_required
# def survey():
#     # username_form = UpdateUsernameForm()

#     form = SurveyForm()

#     if form.validate_on_submit():
#         # User(username=form.username.data, email=form.email.data, password=hashed)
#         # location = Location(address=form.address.data, state=form.state.data, zipcode=form.zipcode.data)
#         survey = Survey(appeal=form.data)
#         return redirect(url_for("users.account"))

#     return render_template("survey.html", survey_form = form)
