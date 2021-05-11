from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import movie_client, mail
from ..forms import MovieReviewForm, SearchForm, LocationForm, SurveyForm
from ..models import User, Review, Location, Survey
from ..utils import current_time

movies = Blueprint('movies', __name__)

@movies.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("movies.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)


@movies .route("/search-results/<query>", methods=["GET"])
def query_results(query):
    result = Location.objects(address__icontains=query)


    return render_template("query.html", results = result)

# @movies.route("/search-results/<query>", methods=["GET"])
# def query_results(query):
#     try:
#         results = movie_client.search(query)
#     except ValueError as e:
#         flash(str(e))
#         return redirect(url_for("movies.index"))

#     return render_template("query.html", results=results)


@movies.route("/movies/<movie_id>", methods=["GET", "POST"])
def movie_detail(movie_id):
    try:
        result = movie_client.retrieve_movie_by_id(movie_id)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("users.login"))

    form = MovieReviewForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            imdb_id=movie_id,
            movie_title=result.title,
        )
        review.save()

        return redirect(request.path)

    reviews = Review.objects(imdb_id=movie_id)

    return render_template(
        "movie_detail.html", form=form, movie=result, reviews=reviews
    )


@movies.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)

    return render_template("user_detail.html", username=username, reviews=reviews)


@movies.route("/add", methods=["GET", "POST"])
def add():
    # username_form = UpdateUsernameForm()

    form = LocationForm()

    if form.validate_on_submit():
        # User(username=form.username.data, email=form.email.data, password=hashed)
        location = Location(address=form.address.data, state=form.state.data, zipcode=form.zipcode.data)
        location.save()
        return redirect(url_for("movies.survey"))

    return render_template("add.html", location_form = form)

@movies.route("/survey", methods=["GET", "POST"])
def survey():
    # username_form = UpdateUsernameForm()

    form = SurveyForm()

    if form.validate_on_submit():
        # User(username=form.username.data, email=form.email.data, password=hashed)
        # location = Location(address=form.address.data, state=form.state.data, zipcode=form.zipcode.data)
        survey = Survey(appeal=form.data)
        return redirect(url_for("users.login"))

    return render_template("survey.html", survey_form = form)

@movies.route("/about", methods=["GET", "POST"])
def about():

    return render_template("about.html")