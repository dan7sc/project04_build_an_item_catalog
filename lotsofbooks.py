from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Bookstore, Base, Book, User


engine = create_engine('sqlite:///virtualbookstores.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

user1 = User(name="Daniel Santiago",
			 email="dansan@fake.com",
			 picture="")
session.add(user1)
session.commit()

bookstore1 = Bookstore(user_id=1,
				   name="Urban Fantasy")
session.add(bookstore1)
session.commit()

book1 = Book(title="The Hobbit",
			 author="J.R.R. Tolkien",
			 genre="Fantasy",
			 description="A book about fantasy.",
			 price="$11.99",
			 bookstore=bookstore1)
session.add(book1)
session.commit()

book2 = Book(title="The Fellowship of the Ring",
			 author="J.R.R. Tolkien",
			 genre="Fantasy",
			 description="A book about fantasy.",
			 price="$13.99",
			 bookstore=bookstore1)
session.add(book2)
session.commit()

book3 = Book(title="The Two Towers",
			 author="J.R.R. Tolkien",
			 genre="Fantasy",
			 description="A book about fantasy.",
			 price="$12.99",
			 bookstore=bookstore1)
session.add(book3)
session.commit()

book4 = Book(title="The Return of the King",
			 author="J.R.R. Tolkien",
			 genre="Fantasy",
			 description="A book about fantasy.",
			 price="$15.99",
			 bookstore=bookstore1)
session.add(book4)
session.commit()


bookstore2 = Bookstore(user_id=1,
				   name="Dead Fish")
session.add(bookstore2)
session.commit()

book1 = Book(title="Sherlock Holmes: Selected Stories",
			 author="Arthur Conan Doyle",
			 genre="Mystery",
			 description="A Sherlock Holmes mystery.",
			 price="$13.39",
			 bookstore=bookstore2)
session.add(book1)
session.commit()

book2 = Book(title="The Murder of Roger Ackroyd",
			 author="Agatha Christie",
			 genre="Mystery",
			 description="A Hercule Poirot mystery.",
			 price="$13.39",
			 bookstore=bookstore2)
session.add(book2)
session.commit()

book3 = Book(title="The Murder on the Links",
			 author="Agatha Christie",
			 genre="Mystery",
			 description="A Hercule Poirot mystery.",
			 price="$12.19",
			 bookstore=bookstore2)
session.add(book3)
session.commit()

bookstore3 = Bookstore(user_id=1,
				   name="Classic Stars")
session.add(bookstore3)
session.commit()

book1 = Book(title="The Red and the Black",
			 author="Stendhal",
			 genre="French Literature",
			 description="A classic book.",
			 price="$23.39",
			 bookstore=bookstore3)
session.add(book1)
session.commit()

book2 = Book(title="Crime and Punishment",
			 author="Fyodor Dostoyevsky",
			 genre="Russian Literature",
			 description="A classic book.",
			 price="$25.09",
			 bookstore=bookstore3)
session.add(book2)
session.commit()

book3 = Book(title="One Hundred Years of Solitude",
			 author="Gabriel Garcia Marquez",
			 genre="Spanish Literature",
			 description="A classic book.",
			 price="$24.19",
			 bookstore=bookstore3)
session.add(book3)
session.commit()

bookstore4 = Bookstore(user_id=1,
				   name="Tupi or not Tupi?")
session.add(bookstore4)
session.commit()

book1 = Book(title="The Third Bank of the River and Other Stories",
			 author="João Guimarães Rosa",
			 genre="Brazilian Literature",
			 description="A brazilian book.",
			 price="$15.39",
			 bookstore=bookstore4)
session.add(book1)
session.commit()

bookstore5 = Bookstore(user_id=1,
				   name="Updated!")
session.add(bookstore5)
session.commit()

book1 = Book(title="Atonement",
			 author="Ian McEwan",
			 genre="British Literature",
			 description="A novel.",
			 price="$16.89",
			 bookstore=bookstore5)
session.add(book1)
session.commit()


print("added books to bookstores!")

