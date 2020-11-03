import os
import datetime

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///test.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32))

# Although cookies can be set for only the browser session, there is nothing stopping a user from modifying 
# the cookie. Therefore, we define an expiry time for session only logins, just to be safe.
SESSION_AUTH_TIME = datetime.timedelta(days=1)
# How long should the cookie be valid for when the user selects remember me
PERMANENT_SESSION_LIFETIME = datetime.timedelta(weeks=16)
 