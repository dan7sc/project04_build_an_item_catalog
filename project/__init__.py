from flask import Flask
from .views.bookstore import bookstore


app = Flask(__name__)

app.register_blueprint(bookstore)