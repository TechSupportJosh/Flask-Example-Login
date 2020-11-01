import datetime
from flask import Flask, render_template, g, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Initialise Flask application and load config
app = Flask(__name__)

app.config.from_object("config")

# Initialise database
db = SQLAlchemy(app)

# Import models after db has been initialised
from models import User, CookieAuth

# Create tables in DB - done after the models have been imported
db.create_all()

# Import decorators
from decorators import login_required

@app.route("/")
def index_page():
    return render_template("index.html", user=g.user)

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")
    else:
        # Retrieve username and password from form
        username = request.form.get("username", None)
        password = request.form.get("password", None)

        if username is None or password is None:
            return redirect(request.url)
        
        # Find the user they're attempting to login as
        user = User.query.filter(User.username == username).first()

        if user is None:
            return redirect(request.url)
        
        # Check the password
        if user.verify_password(password):
            # Password was valid, create a CookieAuth
            expiry_time = datetime.datetime.now() + datetime.timedelta(days=1)
            cookie = CookieAuth(user.user_id, expiry_time)
            db.session.add(cookie)
            db.session.commit()

            # Now set the cookie for the response
            response = redirect(url_for("index_page"))
            response.set_cookie("auth", "{}${}".format(user.user_id, cookie.auth_token), expires=expiry_time)

            return response
        else:
            return redirect(request.url)

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Retrieve username and password from form
        username = request.form.get("username", None)
        password = request.form.get("password", None)

        if username is None or password is None:
            return redirect(request.url)
        
        # Check no user already exists with this username
        user = User.query.filter(User.username == username).first()

        if user is not None:
            return redirect(request.url)
        
        # Check their password is at least 6 characters and their username is at least 4 characters
        if len(password) < 6 or len(username) < 3 or len(username) > 32:
            return redirect(request.url)
        
        # If everything is good, create the user.
        user = User(username, password)
        
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login_page"))

@app.route("/logout")
def logout_page():
    response = redirect(url_for("index_page"))

    # Firstly, check if they're actually logged in
    if g.user is not None:
        # Now revoke the cookie auth they're currently logged in with
        db.session.delete(g.user_cookie_auth)
        db.session.commit()

        # and clear the cookie...
        response.set_cookie("auth", "", max_age=0)

    # Now redirect to index page
    return response