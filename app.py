from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Bookstore, Book, User

app = Flask(__name__)

engine = create_engine('sqlite:///virtualbookstores.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/hello')
def HelloWorld():
	bookstore = session.query(Bookstore).first()
	books = session.query(Book).filter_by(bookstore_id=bookstore.id)
	output = ''
	for i in books:
		output += i.title
		output += '</br>'
		output += i.author
		output += '</br>'
		output += i.genre
		output += '</br>'		
		output += i.price
		output += '</br>'
		output += i.description
		output += '</br>'
		output += '</br>'
	return output

if __name__ == '__main__':
	app.debug = True

app.run(host='0.0.0.0', port=8000)
