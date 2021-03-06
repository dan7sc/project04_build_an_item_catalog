"""
Functions to handle facebook login
"""

from flask import request, flash, make_response
from flask import session as login_session
from flask import Blueprint

import httplib2
import json

from project.models.database_setup import (
    Base, User
    )
from project.models.database_dao import db, dao
from project.views import auth_login


auth_facebook = Blueprint('auth_facebook', __name__,
                          template_folder='templates',
                          static_folder='static')


CLIENT_ID = auth_login.CLIENT_ID


@auth_facebook.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    Description: Connect using facebook login
    Parameters: Nothing
    Return: html code
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data.decode('utf-8')

    app_id = json.loads(
        open(
            'project/models/json/auth/fb_client_secrets.json', 'r'
            ).read())['web']['app_id']
    app_secret = json.loads(
        open(
            'project/models/json/auth/fb_client_secrets.json', 'r'
            ).read())['web']['app_secret']

    url = '''https://graph.facebook.com/oauth/access_token?''' \
        '''grant_type=fb_exchange_token&client_id=%s&client_secret=''' \
        '''%s&fb_exchange_token=%s''' % (app_id, app_secret, access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result.decode('utf-8'))
    token = data['access_token']
    token_type = data['token_type']

    url = '''https://graph.facebook.com/v3.1/me?access_token=%s&''' \
        '''token_type=%s&fields=name,id,email''' % (token, token_type)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result.decode('utf-8'))
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    url = '''https://graph.facebook.com/v3.1/me/picture?''' \
        '''access_token=%s&redirect=0&height=200&width=200''' % token

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result.decode('utf-8'))

    login_session['picture'] = data["data"]["url"]

    user_id = dao.getUserID(db, login_session['email'])
    if not user_id:
        user_id = dao.createUser(db, login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" width: "100px" height: "100px" style = " border-radius: 100px; '
    output += '-webkit-border-radius: 100px; -moz-border-radius: 100px;"> '

    if (login_session['username'] != ''):
        username_unknown = login_session['username']
    else:
        username_unknown = "unknown"
    flash("You are now logged in as %s" % username_unknown)

    print("done!")
    return output


@auth_facebook.route('/fbdisconnect')
def fbdisconnect():
    """
    Description: Disconnect from a facebook login
    Parameters: Nothing
    Return: string
    """
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['facebook_id']
    return "You have been logged out."
