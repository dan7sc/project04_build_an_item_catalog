"""
Functions to deal with books data and information
"""

from flask import (
    render_template, request, make_response,
    redirect, url_for, jsonify, flash
    )
from flask import session as login_session
from flask import Blueprint

from sqlalchemy import asc
from sqlalchemy.orm import sessionmaker

import json

from project.models.database_setup import (
    Base, Bookstore, Book, User
    )
from project.views.auth_login import login_required
from project.models.database_dao import db, file, dao


book = Blueprint('book', __name__,
                 template_folder='templates',
                 static_folder='static')


@book.route('/bookstore/<int:bookstore_id>/')
def bookstoreCatalog(bookstore_id):
    """
    Description: Show all books from a bookstore
    Parameters: bookstore_id
    Return: html page
    """
    session = db.open_session()
    bookstore = session.query(
        Bookstore).filter_by(id=bookstore_id).one_or_none()
    creator = dao.getUserInfo(db, bookstore.user_id)
    books = session.query(Book).filter_by(bookstore_id=bookstore.id).all()
    db.close_session(session)
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
    """
    Description: Create a new book
    Parameters: bookstore id
    Return: html page
    """
    session = db.open_session()
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
        db.close_session(session)
        return redirect(url_for('book.bookstoreCatalog',
                                bookstore_id=bookstore_id))
    else:
        db.close_session(session)
        return render_template('book/newBook.html', bookstore_id=bookstore_id)


@book.route(
    '/bookstore/<int:bookstore_id>/<int:book_id>/edit/',
    methods=['GET', 'POST'])
@login_required
def editBookDetails(bookstore_id, book_id):
    """
    Description: Edit a book detail
    Parameters: bookstore id, book id
    Return: html page
    """
    session = db.open_session()
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
        db.close_session(session)
        return redirect(url_for('book.bookstoreCatalog',
                                bookstore_id=bookstore_id))
    else:
        db.close_session(session)
        return render_template(
            'book/editBookDetails.html', book=editedBook,
            bookstore_id=bookstore_id, book_id=book_id)


@book.route(
    '/bookstore/<int:bookstore_id>/<int:book_id>/delete/',
    methods=['GET', 'POST'])
@login_required
def deleteBook(bookstore_id, book_id):
    """
    Description: Delete a book
    Parameters: bookstore id, book id
    Return: html page
    """
    session = db.open_session()
    deletedBook = session.query(Book).filter_by(id=book_id).one_or_none()
    if deletedBook.user_id != login_session['user_id']:
        return render_template('auth/notOwner.html')
    if(request.method == 'POST'):
        session.delete(deletedBook)
        session.commit()
        books = session.query(Book).all()
        file.updateJSON('project/models/json/database/books.json', books)
        flash("Book %s successfully deleted" % deletedBook.title)
        db.close_session(session)
        return redirect(url_for('book.bookstoreCatalog',
                                bookstore_id=bookstore_id))
    else:
        db.close_session(session)
        return render_template(
            'book/deleteBook.html', book=deletedBook,
            bookstore_id=bookstore_id, book_id=book_id)


@book.route('/bookstore/catalog/JSON')
def catalogJSON():
    """
    Description: Show all books in json format
    Parameters: Nothing
    Return: response
    """
    data_json = json.load(open('project/models/json/database/books.json', 'r'))
    data = json.dumps({"Books": data_json})
    response = make_response(data, 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@book.route('/bookstore/catalog/<int:book_id>/JSON')
def catalogBookJSON(book_id):
    """
    Description: Show a book in json format
    Parameters: book id
    Return: response
    """
    data_json = json.load(open('project/models/json/database/books.json', 'r'))
    data = json.dumps({"Book": data_json[book_id-1]})
    response = make_response(data, 200)
    response.headers['Content-Type'] = 'application/json'
    return response
