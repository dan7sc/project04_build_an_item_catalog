from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import (
    Bookstore, Base, Book, User
    )

import json

engine = create_engine('sqlite:///virtualbookstores.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


user_json = json.loads(
    open('users.json', 'r').read())
bookstore_json = json.loads(
    open('bookstores.json', 'r').read())
book_json = json.loads(
    open('books.json', 'r').read())


for i in user_json['Users']:
    user_input = User(
        id=i['id'],
        name=str(i['name']),
        email=str(i['email']),
        picture=str(i['picture'])
        )
    session.add(user_input)


for i in bookstore_json['Bookstores']:
    bookstore_input = Bookstore(
        id=i['id'],
        name=str(i['name']),
        user_id=i['user_id']
        )
    session.add(bookstore_input)


for i in book_json['Books']:
    book_input = Book(
        id=i['id'],
        title=str(i['title']),
        author=str(i['author']),
        genre=str(i['genre']),
        description=str(i['description']),
        price=str(i['price']),
        bookstore_id=i['bookstore_id'],
        user_id=i['user_id']
        )
    session.add(book_input)


try:
    session.commit()
except Exception:
    session.rollback()
    raise
finally:
    session.close()


print("added books to bookstores!")
