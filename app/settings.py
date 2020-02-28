'''Settings module for system-wide defaults and other values.

Some of the values in this module are used to configure Flask
application instances. (See: config.py)
'''

from os import environ, listdir
from os.path import abspath, join, dirname, isdir


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


# This tuple builds a list of all the Python packages under the `models`
# package. These are associated with Postgres schemas in the database
# backend. Although SQLite does not support schemas (in the Postgres
# sense of the term), we must ensure something similar exists in SQLite
# for unit tests to work correctly. In our app's case, there're no sub-
# packages, so we include `public` as a default non-empty tuple when
# we fail to find packages under `models`, but you'll definitely have
# component-specific packages in larger apps, and organizing those under
# database schemas will be useful in the long-term.
#
# This is a unit test-specific workaround to find schemas in SQLite. For
# more, see the top-level `__init__.py` file.
#
# NOTE: Postgres schemas should be named after their associated Python
# packages to keep things organized. There should be a 1:1 relationship
# between Python package names under the `models` package and Postgres
# schemas containing the backing objects (e.g. model-specific tables).
DATABASE_SCHEMAS = tuple((
    # get directories under `models` that are not private
    f for f in listdir(join(BASE_DIR, 'models'))
    if not f.startswith('_') and isdir(join(BASE_DIR, 'models', f))
)) or ('public',)
