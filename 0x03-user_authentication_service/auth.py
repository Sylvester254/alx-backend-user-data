#!/usr/bin/env python3
"""
This module contains the methods and attributes needed
for the authentication
"""
import bcrypt
from db import User, DB


def _hash_password(password: str) -> bytes:
        """Hash a password with bcrypt
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password

class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Register a new user with the given email and password.
        """
        try:
            user = self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists.")
        except ValueError:
            pass

        hashed_password = self._hash_password(password)
        user = User(email=email, hashed_password=hashed_password)
        self._db.add_user(user)
        return user