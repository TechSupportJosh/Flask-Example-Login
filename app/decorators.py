from functools import wraps
from flask import g, request, redirect, url_for, session, flash
from sqlalchemy import and_

from app import app
from models import CookieAuth, User

import datetime

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if g.user is None (i.e. they're not logged in)
        if g.user is None:
            # Set login redirect to the URL they tried accessing
            session["login_redirect"] = request.url

            flash("You must be logged in to access this page.", "danger")

            # Redirect to the login page
            return redirect(url_for("login_page"))

        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_user_from_cookie():
    g.user = None
    
    # Retrieve the user from the cookie value
    if (auth_cookie := request.cookies.get("auth", None)) is not None:
        # Format of our auth token is user_id$auth_token

        try:
            user_id, auth_token = auth_cookie.split("$")

            # We can safely convert to int() since if they pass an invalid int, it throws ValueError

            # Now search for a valid CookieAuth
            cookie_auth = CookieAuth.query.filter(and_(CookieAuth.user_id == int(user_id), CookieAuth.auth_token == auth_token, CookieAuth.expiry_time > datetime.datetime.now())).first()

            # If a valid auth exists, update g.user to contain the user
            if cookie_auth is not None:
                g.user = User.query.filter(CookieAuth.user_id == int(user_id)).first()
                g.user_cookie_auth = cookie_auth
                
        except ValueError:
            # Cookie is of unknown/incorrect format
            pass