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
    if(request.method == 'POST'):
        session = db.open_session()
        bookstores = session.query(Bookstore).all()
        newBookstore = Bookstore(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newBookstore)
        session.commit()
        bookstores = session.query(Bookstore).all()
        file.updateJSON('project/models/json/database/bookstores.json', bookstores)
        flash("New bookstore %s successfully created" % newBookstore.name)
        db.close_session(session)       
        return redirect(url_for('bookstore.showBookstores'))
    else:
        return render_template('bookstore/newBookstore.html')


@bookstore.route("/bookstore/<int:bookstore_id>/edit/",
                 methods=['GET', 'POST'])
@login_required
def editBookstore(bookstore_id):
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
        file.updateJSON('project/models/json/database/bookstores.json', bookstores)       
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
    session = db.open_session()
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
        db.close_session(session)
        return redirect(url_for('bookstore.showBookstores'))
    else:
        db.close_session(session)
        return render_template(
            'bookstore/deleteBookstore.html',
            bookstore=deletedBookstore, bookstore_id=bookstore_id)


@bookstore.route('/bookstores/JSON')
def bookstoresJSON():
    data_json = json.load(open('project/models/json/database/bookstores.json', 'r'))
    data = json.dumps({"Bookstores": data_json})
    response = make_response(data, 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@bookstore.route('/bookstore/<int:bookstore_id>/JSON')
def bookstoreCatalogJSON(bookstore_id):
    data_json = json.load(open('project/models/json/database/bookstores.json', 'r'))
    data = json.dumps({"Bookstore": data_json[bookstore_id-1]})
    response = make_response(data, 200)
    response.headers['Content-Type'] = 'application/json'
    return response


'''
@bookstore.route('/bookstore/<int:bookstore_id>/catalog/JSON')
def bookstoreCatalogJSON(bookstore_id):
    session = db.open_session()
    bookstore = session.query(
        Bookstore).filter_by(id=bookstore_id).one_or_none()
    books = session.query(Book).filter_by(bookstore_id=bookstore_id).all()
    db.close_session(session)
    return jsonify(Books=[i.serialize for i in books])


@bookstore.route('/bookstores/JSON')
def bookstoresJSON():
    session = db.open_session()
    bookstores = session.query(Bookstore).all()
    db.close_session(session)
    return jsonify(Bookstores=[i.serialize for i in bookstores])


@bookstore.route('/bookstores/J/')
def bookstoresJ():
    session = db.open_session()
    bookstores = session.query(Bookstore).all()
    db.close_session(session)

    bookstores = [i.serialize for i in bookstores]
    Bookstores = {"Bookstores": bookstores}
    tstring = json.dumps(Bookstores, indent=4)
    print(type(tstring))
    file = open('project/models/json/test.json', 'w')
    file.write(tstring)
    file.close()
    # data = str(Bookstores)
    print(Bookstores)
    print(type(Bookstores))
    # data = json.dumps(bookstores)
    # print(type(data))
    # print(data)
    # with open('project/models/json/bookstores.json') as f:
    # data = json.loads(data)
    # print("--", data)

    data = open('project/models/json/bookstores.json', 'r').read()
    # json.dumps(data, open('project/models/json/bookstores.json', 'r'))
    print("**--*", data)
    print(type(data))
    tdata = json.dumps(data, indent=4)
    response = make_response(tdata, 200)
    response.headers['Content-Type'] = 'application/json'
    print(response)
    print(type(response))
    return response


@bookstore.route('/bookstores/JX/')
def bookstoresJX():
    session = db.open_session()
    bookstores = session.query(Bookstore).all()
    db.close_session(session)
    bookstores = [i.serialize for i in bookstores]
    Bookstores = {"Bookstores": bookstores}
    data = json.dumps(Bookstores, indent=4)
    file = open('project/models/json/database/bookstores.json', 'w')
    file.write(data)
    file.close()
    data_json = json.load(
        open('project/models/json/database/bookstores.json',
             'r', encoding='utf-8'))
    data = json.dumps(data_json, indent=4)

    response = make_response(data, 200)
    response.headers['Content-Type'] = 'application/json'
    print(response)
    print(type(response))
    return response


@app.route('/bookstores/JSON')
def bookstoresJSON():
    session = open_session(engine)
    bookstores = session.query(Bookstore).all()
    close_session(session)
    #return jsonify(bookstores=[i.serialize for i in bookstores])
    result = ", ".join(str(i.serialize) for i in bookstores)
    #resultJSON = {'all_results': result}
    print(type(result))
    res = json.dumps(result)
    print(type(res))
    print(res)
    resJ = json.loads(res)
    print(type(resJ))
    return resJ

@app.route('/bookstores/JSON')
def bookstoresJSON():
    bookstores = json.loads(open('bookstores.json', 'r').read())
    print(bookstores)
    bookstores = json.dumps(bookstores)
    return bookstores

'''
