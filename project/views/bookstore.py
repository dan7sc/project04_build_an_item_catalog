from flask import (
    render_template, request, make_response,
    redirect, url_for, jsonify, flash
    )
from sqlalchemy import asc, create_engine
from sqlalchemy.orm import sessionmaker
from project.models.database_setup import (
    Base, Bookstore, Book, User
    )
import json

from flask import session as login_session

from functools import wraps

from flask import Blueprint


engine = create_engine('sqlite:///virtualbookstores.db')


bookstore = Blueprint('bookstore', __name__,
                      template_folder='templates',
                      static_folder='static')


def open_session(engine):
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def close_session(session):
    session.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("Sorry, You Are Not Allowed to Access This Page.")
            return redirect('/login')
    return decorated_function


@bookstore.route('/')
@bookstore.route('/bookstores/')
def showBookstores():
    session = open_session(engine)
    bookstores = session.query(Bookstore).order_by(asc(Bookstore.name))
    close_session(session)
    if 'username' not in login_session:
        return render_template(
            'bookstore/publicBookstores.html', bookstores=bookstores
            )
    else:
        return render_template(
            'bookstore/bookstores.html', bookstores=bookstores
            )


@bookstore.route("/bookstore/new/", methods=['GET', 'POST'])
@login_required
def newBookstore():
    if(request.method == 'POST'):
        session = open_session(engine)
        bookstores = session.query(Bookstore).all()
        newBookstore = Bookstore(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newBookstore)
        session.commit()
        bookstores = session.query(Bookstore).all()
        file.updateJSON('project/models/json/database/bookstores.json', bookstores)
        flash("New bookstore %s successfully created" % newBookstore.name)
        close_session(session)       
        return redirect(url_for('bookstore.showBookstores'))
    else:
        return render_template('bookstore/newBookstore.html')


@bookstore.route("/bookstore/<int:bookstore_id>/edit/",
                 methods=['GET', 'POST'])
@login_required
def editBookstore(bookstore_id):
    session = open_session(engine)
    editedBookstore = session.query(
        Bookstore).filter_by(id=bookstore_id).one_or_none()
    if editedBookstore.user_id != login_session['user_id']:
        return render_template('auth/notOwner.html')
    if(request.method == 'POST'):
        if(request.form['name']):
            editedBookstore.name = request.form['name']
        session.add(editedBookstore)
        session.commit()
        bookstores = session.query(Bookstore).all()
        file.updateJSON('project/models/json/database/bookstores.json', bookstores)       
        flash("Bookstore successfully edited")
        close_session(session)
        return redirect(url_for('bookstore.showBookstores'))
    else:
        close_session(session)
        return render_template(
            'bookstore/editBookstore.html',
            bookstore=editedBookstore, bookstore_id=bookstore_id)


@bookstore.route("/bookstore/<int:bookstore_id>/delete/",
                 methods=['GET', 'POST'])
def deleteBookstore(bookstore_id):
    session = open_session(engine)
    deletedBookstore = session.query(
        Bookstore).filter_by(id=bookstore_id).one_or_none()
    if deletedBookstore.user_id != login_session['user_id']:
        return render_template('auth/notOwner.html')
    if(request.method == 'POST'):
        session.delete(deletedBookstore)
        session.commit()
        bookstores = session.query(Bookstore).all()
        file.updateJSON('project/models/json/database/bookstores.json', bookstores)
        books = session.query(Book).all()
        file.updateJSON('project/models/json/database/books.json', books)
        flash("Bookstore %s successfully deleted" % deletedBookstore.name)
        close_session(session)
        return redirect(url_for('bookstore.showBookstores'))
    else:
        close_session(session)
        return render_template(
            'bookstore/deleteBookstore.html',
            bookstore=deletedBookstore, bookstore_id=bookstore_id)

@bookstore.route('/bookstore/<int:bookstore_id>/catalog/JSON')
def bookstoreCatalogJSON(bookstore_id):
    session = open_session(engine)
    bookstore = session.query(
        Bookstore).filter_by(id=bookstore_id).one_or_none()
    books = session.query(Book).filter_by(bookstore_id=bookstore_id).all()
    close_session(session)
    return jsonify(Books=[i.serialize for i in books])


@bookstore.route('/bookstores/JSON')
def bookstoresJSON():
    session = open_session(engine)
    bookstores = session.query(Bookstore).all()
    close_session(session)
    return jsonify(Bookstores=[i.serialize for i in bookstores])
