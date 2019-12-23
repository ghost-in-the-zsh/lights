'''Settings module for system-wide defaults and other values.

Some of the values in this module are used to configure Flask
application instances. (See: config.py)
'''

from os import environ
from os.path import abspath, join, dirname


# This version string is for informational purposes only (e.g. show in
# the web-ui, etc).
VERSION = '0.1.0'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = abspath(dirname(__file__))

# The instance directory is, by convention, meant to be ignored by Git.
# It contains information that's specific to the running instance, such
# the production or development database (when using SQLite), as well as
# the actual environment `.flaskenv` file.
INSTANCE_DIR = join(dirname(BASE_DIR), 'instance')

# SECURITY WARNING: don't run with debug turned on in production!
# See: conf/uwsgi.ini
FLASK_ENV = environ.get('FLASK_ENV', 'production')

# Name length limits for database objects.
MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 32

# Configuration data for using the Postgres database server. Most of the
# data is stored in environment variables for simplicity. For `docker secrets`
# you'd need to set up a docker swarm.
#
# NOTE: These data are ignored when using SQLite3 (e.g. testing).
DATABASE_CONFIG = {
    'host': environ.get('DATABASE_HOST', None),
    'port': environ.get('DATABASE_PORT', None),
    'name': environ.get('DATABASE_NAME', None),
    'user': environ.get('DATABASE_USER', None),
    'password': environ.get('DATABASE_PASSWORD', None),
    'dialect': 'postgres',
    'driver': 'psycopg2'
}
