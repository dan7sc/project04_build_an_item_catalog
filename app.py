from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Bookstore, Book, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

engine = create_engine('sqlite:///virtualbookstores.db')


CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


def open_session(engine):
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def close_session(session):
    session.close()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's"), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if(stored_credentials is not None and gplus_id == stored_gplus_id):
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src=">'
    output += login_session['picture']
    output += '" style = "width: 300px: height: 300px; border-radius: 150px; '
    output += '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '

    flash("You are now logged in as %s" % login_session['username'])
    return output


@app.route("/gdisconnect")
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if(result['status'] == '200'):
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/bookstores/')
def showBookstores():
    session = open_session(engine)
    bookstores = session.query(Bookstore).order_by(asc(Bookstore.name))
    close_session(session)
    if 'username' not in login_session:
        return render_template('publicBookstores.html', bookstores=bookstores)
    else:
        return render_template('bookstores.html', bookstores=bookstores)


@app.route("/bookstore/<int:bookstore_id>/edit/", methods=['GET', 'POST'])
def editBookstore(bookstore_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = open_session(engine)
    editedBookstore = session.query(Bookstore).filter_by(id=bookstore_id).one()
    if(request.method == 'POST'):
        if(request.form['name']):
            editedBookstore.name = request.form['name']
        session.add(editedBookstore)
        session.commit()
        flash("Bookstore successfully edited")
        close_session(session)
        return redirect(url_for('showBookstores'))
    else:
        close_session(session)
        return render_template('editBookstore.html', bookstore=editedBookstore, bookstore_id=bookstore_id)


@app.route("/bookstore/new/", methods=['GET', 'POST'])
def newBookstore():
    if 'username' not in login_session:
        return redirect('/login')    
    if(request.method == 'POST'):
        session = open_session(engine)
        bookstores = session.query(Bookstore).all()
        newBookstore = Bookstore(name = request.form['name'])
        session.add(newBookstore)
        session.commit()
        flash("New bookstore %s successfully created" % newBookstore.name)
        close_session(session)
        return redirect(url_for('showBookstores'))
    else:
        return render_template('newBookstore.html')


@app.route("/bookstore/<int:bookstore_id>/delete/", methods=['GET', 'POST'])
def deleteBookstore(bookstore_id):
    if 'username' not in login_session:
        return redirect('/login')    
    session = open_session(engine)
    deletedBookstore = session.query(Bookstore).filter_by(id=bookstore_id).one()
    if(request.method == 'POST'):
        session.delete(deletedBookstore)
        session.commit()
        flash("Bookstore %s successfully deleted" % deletedBookstore.name)
        close_session(session)
        return redirect(url_for('showBookstores'))
    else:
        close_session(session)
        return render_template('deleteBookstore.html', bookstore = deletedBookstore, bookstore_id = bookstore_id)


@app.route('/bookstore/<int:bookstore_id>/')
def bookstoreCatalog(bookstore_id):
    session = open_session(engine)
    bookstore = session.query(Bookstore).filter_by(id=bookstore_id).one()
    books = session.query(Book).filter_by(bookstore_id=bookstore.id)
    close_session(session)
    if 'username' not in login_session:
        return render_template('publicBookDetails.html', bookstore=bookstore, books=books)
    else:
        return render_template('bookDetails.html', bookstore=bookstore, books=books)


@app.route('/bookstore/<int:bookstore_id>/new/', methods=['GET', 'POST'])
def newBook(bookstore_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session = open_session(engine)
        newBook = Book(title=request.form['title'],
                       author=request.form['author'],
                       description=request.form['description'],
                       price=request.form['price'],
                       genre=request.form['genre'],
                       bookstore_id=bookstore_id)
        session.add(newBook)
        session.commit()
        flash("New book %s successfully created" % newBook.title)
        close_session(session)
        return redirect(url_for('bookstoreCatalog',bookstore_id=bookstore_id))
    else:
    	return render_template('newBook.html',bookstore_id=bookstore_id)


@app.route('/bookstore/<int:bookstore_id>/<int:book_id>/edit/', methods=['GET', 'POST'])
def editBookDetails(bookstore_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')    
    session = open_session(engine)
    editedBook = session.query(Book).filter_by(id=book_id).one()
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
        flash("Book successfully edited")
        close_session(session)
        return redirect(url_for('bookstoreCatalog', bookstore_id=bookstore_id))
    else:
        close_session(session)
        return render_template('editBookDetails.html', book=editedBook, bookstore_id=bookstore_id, book_id=book_id)


@app.route('/bookstore/<int:bookstore_id>/<int:book_id>/delete/', methods=['GET', 'POST'])
def deleteBook(bookstore_id, book_id):
    session = open_session(engine)
    deletedBook = session.query(Book).filter_by(id=book_id).one()
    if(request.method == 'POST'):
        session.delete(deletedBook)
        session.commit()
        flash("Book %s successfully deleted" % deletedBook.title)
        close_session(session)
        return redirect(url_for('bookstoreCatalog', bookstore_id=bookstore_id))
    else:
        close_session(session)
        return render_template('deleteBook.html', book=deletedBook, bookstore_id=bookstore_id, book_id=book_id)


@app.route('/bookstore/<int:bookstore_id>/catalog/JSON')
def bookstoreCatalogJSON(bookstore_id):
    session = open_session(engine)
    bookstore = session.query(Bookstore).filter_by(id=bookstore_id).one()
    books = session.query(Book).filter_by(bookstore_id=bookstore_id).all()
    close_session(session)
    return jsonify(Books=[i.serialize for i in books])


@app.route('/bookstore/<int:bookstore_id>/catalog/<int:book_id>/JSON')
def catalogBookJSON(bookstore_id, book_id):
    session = open_session(engine)
    book = session.query(Book).filter_by(id=book_id).one()
    close_session(session)
    return jsonify(book = book.serialize)


@app.route('/bookstores/JSON')
def bookstoresJSON():
    session = open_session(engine)
    bookstores = session.query(Bookstore).all()
    close_session(session)
    return jsonify(bookstores=[i.serialize for i in bookstores])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
