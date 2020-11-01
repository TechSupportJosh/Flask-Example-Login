from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql.functions import user
from app import db, app
from hmac import compare_digest

import argon2
import secrets

class User(db.Model):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)

    username = Column(String(32))

    password = Column(String(512))

    def __init__(self, username, password):
        self.username = username

        # Hash and salt password using Argon2 (if stumbling upon this code in the future, check Argon2 is still good to use!)
        hasher = argon2.PasswordHasher()
        self.password = hasher.hash(password)

    def verify_password(self, password):
        """Takes in a string password and returns True/False if the password matches the password in the database."""
        hasher = argon2.PasswordHasher()

        if isinstance(password, str):
            password = password.encode()

        try:
            hasher.verify(self.password, password.encode())

            # If no exception was raised, then the password was correct. 
            # We need to check whether the hash is still valid before returning true. We can only do this here 
            # as this is the only time we have the cleartext password
            if hasher.check_needs_rehash(self.password):
                # If it needs rehashing, do so now
                self.password = hasher.hash(password)

                db.session.commit()

            return True

        except (argon2.exceptions.VerifyMismatchError, argon2.exceptions.VerificationError, argon2.exceptions.InvalidHash):
            # Password did not match (or something else went wrong)
            return False

class CookieAuth(db.Model):
    __tablename__ = "cookie_auth"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

    auth_token = Column(String(192))

    expiry_time = Column(DateTime)

    def __init__(self, user_id, expiry_time):
        self.user_id = user_id
        self.expiry_time = expiry_time

        # Generate a random auth token of 96 bytes (192 character length)
        self.auth_token = secrets.token_hex(96)