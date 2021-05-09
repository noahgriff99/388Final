from flask import session, request
import pytest

from types import SimpleNamespace

from flask_app.forms import RegistrationForm, LoginForm, UpdateUsernameForm
from flask_app.models import User

from wtforms.validators import (
 
    ValidationError,
)


def test_register(client, auth):
    """ Test that registration page opens up """
    resp = client.get("/register")
    assert resp.status_code == 200

    response = auth.register()

    assert response.status_code == 200
    user = User.objects(username="test").first()

    assert user is not None


@pytest.mark.parametrize(
    ("username", "email", "password", "confirm", "message"),
    (
        ("test", "test@email.com", "test", "test", b"Username is taken"),
        ("p" * 41, "test@email.com", "test", "test", b"Field must be between 1 and 40"),
        ("username", "test", "test", "test", b"Invalid email address."),
        ("username", "test@email.com", "test", "test2", b"Field must be equal to"),
    ),
)
def test_register_validate_input(auth, username, email, password, confirm, message):

    if message == b"Username is taken":
        auth.register()

    response = auth.register(username, email, password, confirm)

    assert message in response.data


def test_login(client, auth):
    """ Test that login page opens up """
    resp = client.get("/login")
    assert resp.status_code == 200

    auth.register()
    response = auth.login()

    with client:
        client.get("/")
        assert session["_user_id"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
     (
         ("", "test", b"This field is required"),
         ("test", "", b"This field is required"),
         ("test","fake", b"Login failed. Check your username and/or password"),
         ("asdf","test", b"Login failed. Check your username and/or password"),
     )
    )
def test_login_input_validation(client,auth, username, password, message):

    # review = SimpleNamespace(text=comment,submit="Enter Comment")
    # form = MovieReviewForm(formdata=None, obj=review)
    # response = client.post(f"/movies/{guardians_id}", data=form.data, follow_redirects=True)

    auth.register()

    login = SimpleNamespace(username=username, password=password, submit="Login")
    form = LoginForm(formdata=None, obj=login)
    response = client.post("login", data=form.data, follow_redirects=True)

    assert message in response.data


def test_logout(client, auth):
    auth.register()
    auth.login()
    auth.logout()

    resp = client.get("/login")
    assert resp.status_code == 200


def test_change_username(client, auth):
    auth.register()
    auth.login()
    resp = client.get("/account")
    assert resp.status_code == 200

    update = SimpleNamespace(username="update",submit="Update Username")
    form = UpdateUsernameForm(formdate=None, obj=update)
    response = client.post("/account", data=form.data, follow_redirects=True)

    auth.login(username="update",password="test")

    resp = client.get("/account")
    assert b"update" in resp.data

def test_change_username_taken(client, auth):
    auth.register()
    auth.register(username="taken", email="other@test.com")
    
    auth.login()

    with client:
        client.get("/")
        assert session["_user_id"] == "test"
        update = SimpleNamespace(username="taken",submit="Update Username")
        form = UpdateUsernameForm(formdate=None, obj=update)
        response = client.post("/account", data=form.data, follow_redirects=True)

        assert b"That username is already taken" in response.data



@pytest.mark.parametrize(
    ("new_username", "message"), 
    (
        ("",b"This field is required."),
        ("a" * 41, b"Field must be between 1 and 40 characters long."),
    )
)
def test_change_username_input_validation(client, auth, new_username, message):
    auth.register()
    auth.login()
    resp = client.get("/account")
    assert resp.status_code == 200

    update = SimpleNamespace(username=new_username,submit="Update Username")
    form = UpdateUsernameForm(formdate=None, obj=update)
    response = client.post("/account", data=form.data, follow_redirects=True)

    assert message in response.data


