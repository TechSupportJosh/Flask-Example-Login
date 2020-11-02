import datetime
from flask import Flask, render_template, g, request, redirect, url_for, flash
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
            flash("Please provide a username and password!")
            return redirect(request.url)
        
        # Find the user they're attempting to login as
        user = User.query.filter(User.username == username).first()

        if user is None:
            flash("Invalid username or password!")
            return redirect(request.url)
        
        # Check the password
        if user.verify_password(password):
            # Password was valid, create a CookieAuth
            expiry_time = datetime.datetime.now() + datetime.timedelta(days=1)

            # https://github.com/mattupstate/flask-security/blob/4049c0620383f42d37950c7a35af5ddd6df0540f/flask_security/utils.py#L65
            if 'X-Forwarded-For' in request.headers:
                remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
            else:
                remote_addr = request.remote_addr or 'untrackable'

            cookie = CookieAuth(user.user_id, request.headers.get("User-Agent"), remote_addr, expiry_time)
            db.session.add(cookie)
            db.session.commit()

            # Now set the cookie for the response
            response = redirect(url_for("index_page"))
            response.set_cookie("auth", "{}${}".format(user.user_id, cookie.auth_token), expires=expiry_time)

            return response
        else:
            flash("Invalid username or password!")
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
            flash("Please provide a username and password!")
            return redirect(request.url)
        
        # Check no user already exists with this username
        user = User.query.filter(User.username == username).first()

        if user is not None:
            flash("This username is already in use, please try another one!")
            return redirect(request.url)
        
        # Check their password is at least 6 characters 
        if len(password) < 6:
            flash("Please use a password that is 6 characters or longer!")
            return redirect(request.url)

        # and their username is between 4-20 characters
        if len(username) < 4 or len(username) > 20:
            flash("Please use a username that is between 4 and 20 characters!")
            return redirect(request.url)

        # Check username is alphanumeric
        if not username.isalnum():
            flash("Please use an alphanumeric username (a-z, A-Z, 0-9 only)!")
            return redirect(request.url)

        # If everything is good, create the user.
        user = User(username, password)
        
        db.session.add(user)
        db.session.commit()

        flash("Account has been created, please log in.")

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

    flash("You have now been logged out.")

    # Now redirect to index page
    return response