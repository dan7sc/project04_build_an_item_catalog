from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Bookstore, Book, User

app = Flask(__name__)

engine = create_engine('sqlite:///virtualbookstores.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/bookstores/<int:bookstore_id>/')
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


@app.route('/bookstore/<int:bookstore_id>/<int:book_id>/edit/')
def editBookDetails(bookstore_id, book_id):
	return "page to edit a book details."

@app.route('/bookstore/<int:bookstore_id>/<int:book_id>/delete/')
def deleteBook(bookstore_id, book_id):
	return "page to delete a book."


if __name__ == '__main__':
	app.debug = True

app.run(host='0.0.0.0', port=8000)
