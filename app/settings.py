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

# SECURITY WARNING: avoid making the key length value too small!
# Generally, longer keys provide more cryptographic strength, but
# they also incur higher performance costs.
# See: app/config.py
PRIVATE_KEY_LENGTH = 128

# SECURITY WARNING: web forms are protected by CSRF tokens!
# These tokens are used to protect against CSRF attacks and they
# are set to expire after the time period below. Since these
# are for user-facing web-UI forms, there should be enough time
# for the user to work with the form without the token expiring.
#
# Expired tokens cause form validation to fail and any updates
# sent by the users to be rejected.
CSRF_TOKEN_VALIDITY_SECS = 300  # 300 secs = 5 mins

# Name length limits for database objects.
MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 32

# Yes, the falsey spelling is ok:
# https://english.stackexchange.com/questions/109996/is-it-falsy-or-falsey
TRUTHY = (True, 'True', 'true', 't')
FALSEY = (False, 'False', 'false', 'f')


# Configuration data for using the Postgres database server. Most of the
# data is stored in environment variables for simplicity. For `docker secrets`
# you'd need to set up a docker swarm.
#
# NOTE: These data are ignored when using SQLite3 (e.g. testing).
DATABASE_CONFIG = {
    'host': environ.get('LIGHTS_HOST', None),
    'port': environ.get('LIGHTS_PORT', None),
    'name': environ.get('LIGHTS_DB'  , None),
    'user': environ.get('LIGHTS_USER', None),
    'password': environ.get('LIGHTS_PASSWORD', None),
    'dialect': 'postgres',
    'driver': 'psycopg2'
}
