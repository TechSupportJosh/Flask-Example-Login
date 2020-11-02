import os

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///test.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Use a fixed secret key if desired
SECRET_KEY = os.urandom(32)