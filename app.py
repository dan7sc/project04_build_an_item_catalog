from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Bookstore, Book, User

app = Flask(__name__)

engine = create_engine('sqlite:///virtualbookstores.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/bookstores/')
def showBookstores():
  bookstores = session.query(Bookstore).order_by(asc(Bookstore.name))
  return render_template('bookstores.html', bookstores=bookstores)


@app.route("/bookstore/<int:bookstore_id>/edit/", methods=['GET', 'POST'])
def editBookstore(bookstore_id):
    editedBookstore = session.query(Bookstore).filter_by(id=bookstore_id).one()
    print(editedBookstore.name)
    if(request.method == 'POST'):
        if(request.form['name']):
            editedBookstore.name = request.form['name']
        session.add(editedBookstore)
        session.commit()
        return redirect(url_for('showBookstores'))
    else:
        return render_template('editBookstore.html', bookstore=editedBookstore, bookstore_id=bookstore_id)


@app.route("/bookstore/new/", methods=['GET', 'POST'])
def newBookstore():
    if(request.method == 'POST'):
        bookstores = session.query(Bookstore).all()
        newBookstore = Bookstore(name = request.form['name'])
        session.add(newBookstore)
        session.commit()
        return redirect(url_for('showBookstores'))
    else:
        return render_template('newBookstore.html')

@app.route("/bookstore/<int:bookstore_id>/delete/", methods=['GET', 'POST'])
def deleteBookstore(bookstore_id):
    deletedBookstore = session.query(Bookstore).filter_by(id=bookstore_id).one()
    if(request.method == 'POST'):
        session.delete(deletedBookstore)
        session.commit()
        return redirect(url_for('showBookstores'))
    else:
        return render_template('deleteBookstore.html', bookstore = deletedBookstore, bookstore_id = bookstore_id)


@app.route('/bookstore/<int:bookstore_id>/')
def bookstoreCatalog(bookstore_id):
	bookstore = session.query(Bookstore).filter_by(id=bookstore_id).one()
	books = session.query(Book).filter_by(bookstore_id=bookstore.id)
	return render_template('bookDetails.html', bookstore=bookstore, books=books)


@app.route('/bookstore/<int:bookstore_id>/new/', methods=['GET', 'POST'])
def newBook(bookstore_id):
	if request.method == 'POST':
		newBook = Book(title=request.form['title'],
					   author=request.form['author'],
					   description=request.form['description'],
					   price=request.form['price'],
					   genre=request.form['genre'],
					   bookstore_id=bookstore_id)
		session.add(newBook)
		session.commit()
		return redirect(url_for('bookstoreCatalog',bookstore_id=bookstore_id))
	else:
		return render_template('newBook.html',bookstore_id=bookstore_id)


@app.route('/bookstore/<int:bookstore_id>/<int:book_id>/edit/', methods=['GET', 'POST'])
def editBookDetails(bookstore_id, book_id):
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
		return redirect(url_for('bookstoreCatalog', bookstore_id=bookstore_id))
	else:
		return render_template('editBookDetails.html', book=editedBook, bookstore_id=bookstore_id, book_id=book_id)

@app.route('/bookstore/<int:bookstore_id>/<int:book_id>/delete/', methods=['GET', 'POST'])
def deleteBook(bookstore_id, book_id):
	deleteBook = session.query(Book).filter_by(id=book_id).one()
	if(request.method == 'POST'):
		session.delete(deleteBook)
		session.commit()
		return redirect(url_for('bookstoreCatalog', bookstore_id=bookstore_id))
	else:
		return render_template('deleteBook.html', book=deleteBook, bookstore_id=bookstore_id, book_id=book_id)


@app.route('/bookstore/<int:bookstore_id>/catalog/JSON')
def bookstoreCatalogJSON(bookstore_id):
	bookstore = session.query(Bookstore).filter_by(id=bookstore_id).one()
	books = session.query(Book).filter_by(bookstore_id=bookstore_id).all()
	return jsonify(Books=[i.serialize for i in books])


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=8000)
