'''Settings module for system-wide defaults and other values.

Some of the values in this module are used to configure Flask
application instances. (See: config.py)
'''

from os import environ, listdir
from os.path import abspath, join, dirname, isdir


# This version string is for informational purposes only (e.g. show in
# the web-ui, etc). See https://semver.org
VERSION = '0.2.1'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = abspath(dirname(__file__))

# The instance directory is, by convention, meant to be ignored by Git.
# It contains information that's specific to the running instance, such
# the production or development database (when using SQLite), as well as
# the actual environment `.flaskenv` file.
INSTANCE_DIR = join(dirname(BASE_DIR), 'instance')

# SECURITY WARNING: don't run with debug turned on in production!
# See: conf/web/uwsgi.ini
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
CSRF_TOKEN_TTL_SECS = 300  # 300 secs = 5 mins

# Yes, the falsey spelling is ok:
# https://english.stackexchange.com/questions/109996/is-it-falsy-or-falsey
TRUTHY = (True, 'True', 'true', 't')
FALSEY = (False, 'False', 'false', 'f')

# Length limits for string-based database columns/objects.
MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 32

# SECURITY WARNING: Hashes are only as strong as the passwords from which
# they're derived. Therefore, the minimum length of user passwords must
# be reasonably long.
#
# Useful reference:
# NIST Special Publication 800-63B: Digital Identity Guidelines
# https://pages.nist.gov/800-63-3/sp800-63b.html
MIN_PASSWORD_LENGTH = 16
MAX_PASSWORD_LENGTH = 64

# SECURITY WARNING: Passwords are hashed using the Argon2 algorithm[1],
# implemented in the `argon2-cffi` package[2]. Argon2 is able to produce
# hashes of variable length (up to 2^(32)-1 bytes[2]). In encoded format,
# an Argon2 hash looks as follows:
#
#   $<hash>$v=<version>$m=<memory>,t=<time>,p=<parallelism>$<digest>
#
# For example, hashing the word 'password' with the default options:
#
#   hash: argon2id
#   version: 19
#   memory: 102400 (KiB)
#   time: 2
#   parallelism: 8
#   hash_len: 16    (not part of encoded result)
#   salt_len: 16    (not part of encoded result)
#   encoding: utf-8 (not part of encoded result)
#
# generates the encoded result below with 77 chars:
#
#   $argon2id$v=19$m=102400,t=2,p=8$/fyEiWLtEptoby4N1mWtCQ$U4sZg3akPymER4+XV85t5w
#
# The maximum length below was chosen to accomodate this result. If hashes
# need to be upgraded in the future, and the hash length is affected (not
# all changes affect hash lengths), then update the length below and let
# the application automatically upgrade user hashes as they log back in.
#
# For more info, see [3] and [4].
#
# [1] https://en.wikipedia.org/wiki/Argon2
# [2] https://pypi.org/project/argon2-cffi/
# [3] https://password-hashing.net/
# [4] https://github.com/P-H-C/phc-winner-argon2
MAX_PASSWORD_HASH_LENGTH = 77

# SECURITY WARNING: The server-side must always control this.
# There've been some cases where clients have been able to attack servers
# by changing headers, at least in cases where servers failed to validate
# the headers themselves. While the library used in this app is not
# vulnerable to these attacks, it's still worth noting.
#
# https://docs.authlib.org/en/latest/specs/rfc7519.html
# https://en.wikipedia.org/wiki/JSON_Web_Token
AUTH_JWT_HEADER = {
    'alg': 'HS256',     # HMAC + SHA-256
    'typ': 'JWT'
}

# This app is the token issuer.
AUTH_JWT_PAYLOAD_ISS = 'Lights'

# SECURITY WARNING: Tokens should be short-lived and NOT have sensitive data!
# In our context, a token's expiration time should be a few minutes;
# enough for the user to receive an email and click on the included link.
AUTH_JWT_PAYLOAD_EXP = 900  # 900 secs = 15 mins

# Configuration data for using the Postgres database server. Most of the
# data is stored in environment variables for simplicity. For `docker secrets`
# you'd need to set up a docker swarm.
#
# NOTE: These data are ignored when using SQLite3 (e.g. testing).
DATABASE_CONFIG = {
    'host': environ.get('LIGHTS_DB_HOST', None),
    'port': environ.get('LIGHTS_DB_PORT', None),
    'name': environ.get('LIGHTS_DB_NAME', None),
    'user': environ.get('LIGHTS_DB_USER', None),
    'password': environ.get('LIGHTS_DB_PASSWORD', None),
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
