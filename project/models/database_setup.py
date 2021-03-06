"""
Create classes for user, bookstore and book tables
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    """Register columns for user table"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    picture = Column(String(250))


class Bookstore(Base):
    """Register columns for bookstore table"""
    __tablename__ = 'bookstore'

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
        }


class Book(Base):
    """Register columns for book table"""
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    genre = Column(String(100))
    description = Column(String(300))
    price = Column(String(10))
    bookstore_id = Column(Integer, ForeignKey('bookstore.id'))
    bookstore = relationship(Bookstore, backref=backref(
        'bookstore',
        cascade="all, delete-orphan"
        ))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'description': self.description,
            'price': self.price,
            'bookstore_id': self.bookstore_id,
            'user_id': self.user_id
        }


# Connect to Database
engine = create_engine('sqlite:///virtualbookstores.db')
Base.metadata.create_all(engine)
