"""
Functions to deal with bookstores data and information
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
from project.models.database_dao import db, file


bookstore = Blueprint('bookstore', __name__,
                      template_folder='templates',
                      static_folder='static')


@bookstore.route('/')
@bookstore.route('/bookstores/')
def showBookstores():
    """
    Description: Show all bookstores
    Parameters: Nothing
    Return: html page
    """
    session = db.open_session()
    bookstores = session.query(Bookstore).order_by(asc(Bookstore.name))
    db.close_session(session)
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
    """
    Description: Create a new bookstore
    Parameters: Nothing
    Return: html page
    """
    if(request.method == 'POST'):
        session = db.open_session()
        bookstores = session.query(Bookstore).all()
        newBookstore = Bookstore(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newBookstore)
        session.commit()
        bookstores = session.query(Bookstore).all()
        file.updateJSON(
            'project/models/json/database/bookstores.json', bookstores)
        flash("New bookstore %s successfully created" % newBookstore.name)
        db.close_session(session)
        return redirect(url_for('bookstore.showBookstores'))
    else:
        return render_template('bookstore/newBookstore.html')


@bookstore.route("/bookstore/<int:bookstore_id>/edit/",
                 methods=['GET', 'POST'])
@login_required
def editBookstore(bookstore_id):
    """
    Description: Edit a bookstore
    Parameters: bookstore id
    Return: html page
    """
    session = db.open_session()
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
        file.updateJSON(
            'project/models/json/database/bookstores.json', bookstores)
        flash("Bookstore successfully edited")
        db.close_session(session)
        return redirect(url_for('bookstore.showBookstores'))
    else:
        db.close_session(session)
        return render_template(
            'bookstore/editBookstore.html',
            bookstore=editedBookstore, bookstore_id=bookstore_id)


@bookstore.route("/bookstore/<int:bookstore_id>/delete/",
                 methods=['GET', 'POST'])
def deleteBookstore(bookstore_id):
    """
    Description: Delete a bookstore
    Parameters: bookstore id
    Return: html page
    """
    session = db.open_session()
    deletedBookstore = session.query(
        Bookstore).filter_by(id=bookstore_id).one_or_none()
    if deletedBookstore.user_id != login_session['user_id']:
        return render_template('auth/notOwner.html')
    if(request.method == 'POST'):
        session.delete(deletedBookstore)
        session.commit()
        bookstores = session.query(Bookstore).all()
        file.updateJSON(
            'project/models/json/database/bookstores.json', bookstores)
        books = session.query(Book).all()
        file.updateJSON('project/models/json/database/books.json', books)
        flash("Bookstore %s successfully deleted" % deletedBookstore.name)
        db.close_session(session)
        return redirect(url_for('bookstore.showBookstores'))
    else:
        db.close_session(session)
        return render_template(
            'bookstore/deleteBookstore.html',
            bookstore=deletedBookstore, bookstore_id=bookstore_id)


@bookstore.route('/bookstores/JSON')
def bookstoresJSON():
    """
    Description: Show all bookstores in json format
    Parameters: Nothing
    Return: response
    """
    data_json = json.load(open(
        'project/models/json/database/bookstores.json', 'r'))
    data = json.dumps({"Bookstores": data_json})
    response = make_response(data, 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@bookstore.route('/bookstore/<int:bookstore_id>/JSON')
def bookstoreJSON(bookstore_id):
    """
    Description: Show a bookstore in json format
    Parameters: bookstore id
    Return: response
    """
    data_json = json.load(open(
        'project/models/json/database/bookstores.json', 'r'))
    data = json.dumps({"Bookstore": data_json[bookstore_id-1]})
    response = make_response(data, 200)
    response.headers['Content-Type'] = 'application/json'
    return response
