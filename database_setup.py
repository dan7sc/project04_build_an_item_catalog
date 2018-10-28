from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(150), nullable=False)
	email = Column(String(150), nullable=False)
	picture = Column(String(250))


class Bookstore(Base):
	__tablename__ = 'bookstore'

	id = Column(Integer, primary_key=True)
	name = Column(String(150), nullable=False)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		return {
			'id'			: self.id,
			'name'			: self.name,
			'user_id'		: self.user_id,
		}

class Book(Base):
	__tablename__ = 'book'

	id = Column(Integer, primary_key=True)
	title = Column(String(100), nullable=False)
	author = Column(String(100), nullable=False)
	genre = Column(String(100))
	description = Column(String(300))
	price = Column(String(10))
	bookstore_id = Column(Integer, ForeignKey('bookstore.id'))
	bookstore = relationship(Bookstore)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		return {
			'id'			: self.id,
			'title'			: self.title,
			'author'		: self.author,
			'genre'			: self.genre,
			'description'	: self.description,
			'price'			: self.price,
			'bookstore_id'	: self.bookstore_id,
			'user_id'		: self.user_id
		}

engine = create_engine('sqlite:///virtualbookstores.db')

Base.metadata.create_all(engine)
