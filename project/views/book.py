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

from project.views.auth_login import login_required

from flask import Blueprint


engine = create_engine('sqlite:///virtualbookstores.db')


book = Blueprint('book', __name__,
                 template_folder='templates',
                 static_folder='static')


def open_session(engine):
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def close_session(session):
    session.close()



def getUserInfo(user_id):
    session = open_session(engine)
    user = session.query(User).filter_by(id=user_id).one_or_none()
    close_session(session)
    return user


@book.route('/bookstore/<int:bookstore_id>/')
def bookstoreCatalog(bookstore_id):
    session = open_session(engine)
    bookstore = session.query(
        Bookstore).filter_by(id=bookstore_id).one_or_none()
    creator = getUserInfo(bookstore.user_id)
    books = session.query(Book).filter_by(bookstore_id=bookstore.id).all()
    close_session(session)
    if 'username' not in login_session or creator.id != login_session[
        'user_id'
    ]:
        return render_template(
            'book/publicBookDetails.html', bookstore=bookstore, books=books)
    else:
        return render_template(
            'book/bookDetails.html', bookstore=bookstore, books=books)


@book.route('/bookstore/<int:bookstore_id>/new/', methods=['GET', 'POST'])
@login_required
def newBook(bookstore_id):
    session = open_session(engine)
    bookstore = session.query(
        Bookstore).filter_by(id=bookstore_id).one_or_none()
    if bookstore.user_id != login_session['user_id']:
        return render_template('auth/notOwner.html')
    if request.method == 'POST':
        newBook = Book(title=request.form['title'],
                       author=request.form['author'],
                       description=request.form['description'],
                       price=request.form['price'],
                       genre=request.form['genre'],
                       bookstore_id=bookstore_id,
                       user_id=bookstore.user_id)
        session.add(newBook)
        session.commit()
        books = session.query(Book).all()
        file.updateJSON('project/models/json/database/books.json', books)
        flash("New book %s successfully created" % newBook.title)
        close_session(session)
        return redirect(url_for('book.bookstoreCatalog',
                                bookstore_id=bookstore_id))
    else:
        close_session(session)
        return render_template('book/newBook.html', bookstore_id=bookstore_id)


@book.route(
    '/bookstore/<int:bookstore_id>/<int:book_id>/edit/',
    methods=['GET', 'POST'])
@login_required
def editBookDetails(bookstore_id, book_id):
    session = open_session(engine)
    editedBook = session.query(Book).filter_by(id=book_id).one_or_none()
    if editedBook.user_id != login_session['user_id']:
        return render_template('auth/notOwner.html')
    if(request.method == 'POST'):
        if(request.form['title']):
            editedBook.title = request.form['title']
        if(request.form['author']):
            editedBook.author = request.form['author']
        if(request.form['description']):
            editedBook.description = request.form['description']
        if(request.form['genre']):
            editedBook.genre = request.form['genre']
        if(request.form['price']):
            editedBook.price = request.form['price']
        session.add(editedBook)
        session.commit()
        books = session.query(Book).all()
        file.updateJSON('project/models/json/database/books.json', books)        
        flash("Book successfully edited")
        close_session(session)
        return redirect(url_for('book.bookstoreCatalog',
                                bookstore_id=bookstore_id))
    else:
        close_session(session)
        return render_template(
            'book/editBookDetails.html', book=editedBook,
            bookstore_id=bookstore_id, book_id=book_id)


@book.route(
    '/bookstore/<int:bookstore_id>/<int:book_id>/delete/',
    methods=['GET', 'POST'])
@login_required
def deleteBook(bookstore_id, book_id):
    session = open_session(engine)
    deletedBook = session.query(Book).filter_by(id=book_id).one_or_none()
    if deletedBook.user_id != login_session['user_id']:
        return render_template('auth/notOwner.html')
    if(request.method == 'POST'):
        session.delete(deletedBook)
        session.commit()
        books = session.query(Book).all()
        file.updateJSON('project/models/json/database/books.json', books)        
        flash("Book %s successfully deleted" % deletedBook.title)
        close_session(session)
        return redirect(url_for('book.bookstoreCatalog',
                                bookstore_id=bookstore_id))
    else:
        close_session(session)
        return render_template(
            'book/deleteBook.html', book=deletedBook,
            bookstore_id=bookstore_id, book_id=book_id)


@book.route('/bookstore/<int:bookstore_id>/catalog/<int:book_id>/JSON')
def catalogBookJSON(bookstore_id, book_id):
    session = open_session(engine)
    book = session.query(Book).filter_by(id=book_id).one_or_none()
    close_session(session)
    return jsonify(Book=book.serialize)
