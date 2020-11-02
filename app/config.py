import os

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///test.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False