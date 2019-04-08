"""
Run the app on http://localhost:8000/
or http://0.0.0.0:8000/
"""

from project import app


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
