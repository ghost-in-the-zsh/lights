'''WSGI entrypoint module with callable application object.

This module is used by the uWSGI server, as specified in the
uWSGI configuration file.

See: conf/web/uwsgi.ini
'''

from app import create_app
from app.settings import FLASK_ENV

app = create_app(FLASK_ENV)
