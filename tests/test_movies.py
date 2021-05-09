import pytest

from types import SimpleNamespace
import random
import string

from flask_app.forms import SearchForm, MovieReviewForm
from flask_app.models import User, Review


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query="guardians", submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert b"Guardians of the Galaxy" in response.data


@pytest.mark.parametrize(
    ("query", "message"), 
    (
        ("",b"This field is required."),
        ("1",b"Too many results"),
        ("azertg",b"Movie not found!"),
        ('a' * 101, b"Field must be between 1 and 100 characters long.")
    )
)
def test_search_input_validation(client, query, message):

    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query=query,submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert message in response.data


def test_movie_review(client, auth):
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"
    resp = client.get(url)

    assert resp.status_code == 200

    auth.register()
    auth.login()

    testData = ''.join(random.choice(string.ascii_lowercase) for i in range(10))


    review = SimpleNamespace(text=testData,submit="Enter Comment")
    form = MovieReviewForm(formdata=None, obj=review)
    response = client.post(f"/movies/{guardians_id}", data=form.data, follow_redirects=True)

    assert bytes(testData, encoding='utf-8') in response.data

    # reviews = Review.objects(imdb_id=guardians_id)

    # print(reviews)
    # assert testData in reviews
    # assert bytes(testData, encoding='utf-8') in reviews


@pytest.mark.parametrize(
    ("movie_id", "message"), 
    (
        ("1",b"Incorrect IMDb ID"),
        ("123456789",b"Incorrect IMDb ID"),
        ("12345678910",b"Incorrect IMDb ID"),
    )
)
def test_movie_review_redirects(client, movie_id, message):

    resp = client.get(f"/movies/")
    assert resp.status_code == 404

    # resp = client.get(f"/movies/{movie_id}")
    resp = client.post(f"/movies/{movie_id}", data=None, follow_redirects=False)
    assert resp.status_code == 302

    resp = client.post(f"/movies/{movie_id}", data=None, follow_redirects=True)
    assert message in resp.data
   # assert message in resp.data




@pytest.mark.parametrize(
    ("comment", "message"), 
    (
        ("",b"This field is required."),
        ('a',b"Field must be between 5 and 500 characters long"),
        ('a' * 501,b"Field must be between 5 and 500 characters long"),
    )
)
def test_movie_review_input_validation(client, auth, comment, message):
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"
    resp = client.get(url)

    assert resp.status_code == 200

    auth.register()
    auth.login()

    review = SimpleNamespace(text=comment,submit="Enter Comment")
    form = MovieReviewForm(formdata=None, obj=review)
    response = client.post(f"/movies/{guardians_id}", data=form.data, follow_redirects=True)

    assert message in response.data

