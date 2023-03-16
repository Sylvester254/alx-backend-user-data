#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from user import Base, User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session
    
    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user
    
    def find_user_by(self, **kwargs) -> User:
        """Find a user in the database based on input arguments
        """
        try:
            user = self._session.query(User).filter_by(**kwargs).first()
            if not user:
                raise NoResultFound("No user found with the given arguments")
            return user
        except InvalidRequestError as e:
            self._session.rollback()
            raise e

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update a user's attributes in the database
        """
        user = self.find_user_by(id=user_id)
        for attr, value in kwargs.items():
            if not hasattr(user, attr):
                raise ValueError(f"{attr} is not a valid attribute for User")
            setattr(user, attr, value)
        self._session.commit()