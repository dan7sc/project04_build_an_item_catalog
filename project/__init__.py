from flask import Flask
from flask_seasurf import SeaSurf

from .views.bookstore import bookstore
from .views.book import book
from .views.auth_login import auth_login
from .views.auth_google import auth_google



app = Flask(__name__)

app.register_blueprint(bookstore)
app.register_blueprint(book)
app.register_blueprint(auth_login)
app.register_blueprint(auth_google)

csrf = SeaSurf(app)
csrf._csrf_disable = False
csrf.exempt_urls(('/gconnect', '/fbconnect',))
