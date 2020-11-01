from flask import Flask
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
