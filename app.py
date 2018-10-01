from flask import Flask, render_template
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

@app.route('/bookstore/<int:bookstore_id>/new/')
def newBook(bookstore_id):
	return "page to create a new book."

@app.route('/bookstore/<int:bookstore_id>/<int:book_id>/edit/')
def editBookDetails(bookstore_id, book_id):
	return "page to edit a book details."

@app.route('/bookstore/<int:bookstore_id>/<int:book_id>/delete/')
def deleteBook(bookstore_id, book_id):
	return "page to delete a book."


if __name__ == '__main__':
	app.debug = True

app.run(host='0.0.0.0', port=8000)
