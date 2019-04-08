"""
Function to handle login
"""

from flask import render_template, redirect, flash
from flask import session as login_session
import random
import string
import json
from flask import Blueprint
from functools import wraps


auth_login = Blueprint('auth_login', __name__,
                       template_folder='templates',
                       static_folder='static')


CLIENT_ID = json.loads(
    open('project/models/json/auth/client_secrets.json', 'r').read()
    )['web']['client_id']


@auth_login.route('/login')
def showLogin():
    """
    Description: Direct to the login page
    Parameters: Nothing
    Return: html page
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('auth/login.html', STATE=state, CLIENT_ID=CLIENT_ID)


def login_required(f):
    """
    Description: Disconnect from a login session
    Parameters: function
    Return: redirect to a html page
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("Sorry, You Are Not Allowed to Access This Page.")
            return redirect('/login')
    return decorated_function
