from flask import redirect, url_for, flash
from flask import session as login_session

from flask import Blueprint

from project.views import auth_google
from project.views import auth_facebook


auth_logout = Blueprint('auth_logout', __name__,
                        template_folder='templates',
                        static_folder='static')


@auth_logout.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            auth_google.gdisconnect()
        if login_session['provider'] == 'facebook':
            auth_facebook.fbdisconnect()
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('bookstore.showBookstores'))
    else:
        flash("You were not logged in.")
        return redirect(url_for('bookstore.showBookstores'))
