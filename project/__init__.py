from flask import Flask
from .views.bookstore import bookstore
from .views.book import book


app = Flask(__name__)

app.register_blueprint(bookstore)
app.register_blueprint(book)
