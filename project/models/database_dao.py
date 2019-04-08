"""
Create helper classes to deal with db data
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import json

from project.models.database_setup import Base, User


class daoSessionClass():
    """Helper class to handle session"""
    def __init__(self, db_path):
        """Constructor"""
        self.engine = create_engine(db_path)
        Base.metadata.bind = self.engine
        self.DBSession = sessionmaker(bind=self.engine)

    def open_session(self):
        """
        Description: Open a session
        Parameters: Nothing
        Return: Nothing
        """
        self.session = self.DBSession()
        return self.session

    def close_session(self, session):
        """
        Description: Close a session
        Parameters: session
        Return: Nothing
        """
        session.close()


class daoJSONClass():
    """Helper class to handle json"""
    def updateJSON(self, data_path, data):
        """
        Description: Write data to json file
        Parameters: path to json file
        Return: Nothing
        """
        self.data = [i.serialize for i in data]
        self.data_json = json.dumps(self.data)
        self.wfile = open(data_path, 'w')
        self.wfile.write(self.data_json)
        self.wfile.close()


class daoUserClass():
    """Helper class to handle user information"""
    def createUser(self, db, login_session):
        """
        Description: Create a user and
                     stored him in the database
        Parameters: database, login_session
        Return: user id
        """
        self.session = db.open_session()
        self.newUser = User(name=login_session['username'],
                            email=login_session['email'],
                            picture=login_session['picture'])
        self.session.add(self.newUser)
        self.session.commit()
        self.user = self.session.query(User).filter_by(
            email=login_session['email']
            ).one_or_none()
        db.close_session(self.session)
        return self.user.id

    def getUserID(self, db, email):
        """
        Description: Get id from a user
        Parameters: database, user email
        Return: user id or none
        """
        try:
            self.session = db.open_session()
            self.user = self.session.query(
                User).filter_by(email=email).one_or_none()
            db.close_session(self.session)
            return self.user.id
        except Exception:
            return None

    def getUserInfo(self, db, user_id):
        """
        Description: Get information about a user
        Parameters: database, user email
        Return: user
        """
        self.session = db.open_session()
        self.user = self.session.query(
            User).filter_by(id=user_id).one_or_none()
        db.close_session(self.session)
        return self.user


db = daoSessionClass(
    'sqlite:///project/models/virtualbookstores.db'
    )
file = daoJSONClass()
dao = daoUserClass()
