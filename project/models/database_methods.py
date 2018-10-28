from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from project.models.database_setup import Base, User

from flask import session as login_session

from project.models.database_dao import db


engine = create_engine('sqlite:///virtualbookstores.db')


def open_session(engine):
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def close_session(session):
    session.close()


def createUser(login_session):
    session = db.open_session()
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']
        ).one_or_none()
    db.close_session(session)
    return user.id


def getUserID(email):
    try:
        session = db.open_session()
        user = session.query(User).filter_by(email=email).one_or_none()
        db.close_session(session)
        return user.id
    except Exception:
        return None


def getUserInfo(user_id):
    session = db.open_session()
    user = session.query(User).filter_by(id=user_id).one_or_none()
    db.close_session(session)
    return user
