#!/usr/bin/env python3
"""
This module contains the methods and attributes needed
for the authentication
"""
import bcrypt
from db import User, DB
from bcrypt import hashpw, gensalt, checkpw
from db import DB
import uuid
from user import User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from typing import Union


def _hash_password(password: str) -> bytes:
    """Hash a password with bcrypt
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def _generate_uuid() -> str:
    """
    Method that generates a UUID.
    Returns:
        str: The generated UUID.
    """
    return str(uuid.uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Register a new user with the given email and password.
        """
        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            encrypt = _hash_password(password=password)
            return self._db.add_user(email=email, hashed_password=encrypt)
        else:
            raise ValueError("User {} already exists".format(email))

    def valid_login(self, email: str, password: str) -> bool:
        """
        Method that validates a login.
        Args:
            email: The email of the user.
            password: The password of the user.
        Returns:
            bool: True if the login is valid, False otherwise.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False
        else:
            return bcrypt.checkpw(password=password.encode(),
                                  hashed_password=user.hashed_password)

    def create_session(self, email: str) -> Union[str, None]:
        """
        Method that creates a session for a user.
        Args:
            email: The email of the user.
        Returns:
            str: The session id.
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except (NoResultFound, ValueError):
            return None

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """
        Method that gets a user from a session id.
        Args:
            session_id: The session id.
        Returns:
            User: The user object.
        """
        if not session_id:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """
        Method that destroys a session for a user.
        Args:
            user_id: The user id.
        """
        try:
            self._db.update_user(user_id, session_id=None)
        except ValueError:
            pass

    def get_reset_password_token(self, email: str) -> str:
        """
        Method that gets a reset password token.
        Args:
            email: The email of the user.
        Raises:
            ValueError: If the user does not exist.
        Returns:
            str: The reset password token.
        """
        try:
            user = self._db.find_user_by(email=email)
            if user.reset_token:
                return user.reset_token
            token = _generate_uuid()
            self._db.update_user(user.id, reset_token=token)
            return token
        except NoResultFound:
            raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Method that updates the password of a user.
        Args:
            reset_token: The reset password token.
            password: The new password.
        Returns:
            bool: True if the password was updated, False otherwise.
        Raises:
            ValueError: If the reset token is invalid.
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed_password = _hash_password(password).decode('utf-8')
            self._db.update_user(user.id, hashed_password=hashed_password,
                                 reset_token=None)
        except NoResultFound:
            raise ValueError
