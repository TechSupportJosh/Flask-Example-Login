from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql.functions import user
from app import db, app
from hmac import compare_digest

import argon2
import secrets
import datetime

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {'sqlite_autoincrement': True}

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
            hasher.verify(self.password, password)

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
    __table_args__ = {'sqlite_autoincrement': True}

    cookie_auth_id = Column(Integer, primary_key=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey("users.user_id"))

    expiry_time = Column(DateTime)

    # Note that 512 characters won't always be enough, there's always some weird user agents that can appear...
    # See https://stackoverflow.com/questions/654921/how-big-can-a-user-agent-string-get
    user_agent = Column(String(512))
    
    # 39 characters for when IPv6 is used
    ip_address = Column(String(39))

    def __init__(self, user_id, user_agent, ip_address, expiry_time):
        self.user_id = user_id
        self.user_agent = user_agent
        self.ip_address = ip_address
        self.expiry_time = expiry_time

    def has_expired(self):
        """Returns True/False depending on whether this CookieAuth has expired."""
        return datetime.datetime.now() > self.expiry_time