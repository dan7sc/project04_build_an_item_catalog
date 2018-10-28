from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import json

from project.models.database_setup import Base, User


class daoSessionClass():
    def __init__(self, db_path):
        self.engine = create_engine(db_path)
        Base.metadata.bind = self.engine
        self.DBSession = sessionmaker(bind=self.engine)

    def open_session(self):
        self.session = self.DBSession()
        return self.session

    def close_session(self, session):
        session.close()


class daoJSONClass():
    def updateJSON(self, data_path, data):
        self.data = [i.serialize for i in data]
        self.data_json = json.dumps(self.data)
        self.wfile = open(data_path, 'w')
        self.wfile.write(self.data_json)
        self.wfile.close()


class daoUserClass():
    def createUser(self, db, login_session):
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
        try:
            self.session = db.open_session()
            self.user = self.session.query(
                User).filter_by(email=email).one_or_none()
            db.close_session(self.session)
            return self.user.id
        except Exception:
            return None

    def getUserInfo(self, db, user_id):
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
