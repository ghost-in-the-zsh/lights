'''Configuration module for Flask application objects.

The configuration classes describe the properties that should be applied
to Flask application instances, based on their execution environment.
'''

import os

from app.settings import (
    VERSION,
    INSTANCE_DIR,
    PRIVATE_KEY_LENGTH,
    CSRF_TOKEN_VALIDITY_SECS,
    DATABASE_CONFIG
)


class ProductionConfig:
    VERSION = VERSION

    # Flask
    # http://flask.palletsprojects.com/en/1.1.x/config/
    DEBUG = False
    TESTING = False
    # SECURITY WARNING: keep the secret key secret!
    # This provides random bytes that are suitable for cryptographic use.
    # https://docs.python.org/3/library/os.html#os.urandom
    SECRET_KEY = os.urandom(PRIVATE_KEY_LENGTH)

    # Flask-SQLAlchemy
    # https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
    # https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls
    SQLALCHEMY_DATABASE_URI = '%(dialect)s+%(driver)s://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s' % DATABASE_CONFIG
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-DebugToolbar
    # https://flask.palletsprojects.com/en/1.1.x/config/
    DEBUG_TB_ENABLED = False
    DEBUG_TB_PROFILER_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False

    # Flask-WTForms
    # https://flask-wtf.readthedocs.io/en/stable/config.html
    # SECURITY WARNING: web form protection against CSRF attacks!
    WTF_CSRF_TIME_LIMIT = CSRF_TOKEN_VALIDITY_SECS


class DevelopmentConfig(ProductionConfig):
    # Flask overrides
    DEBUG = True
    EXPLAIN_TEMPLATE_LOADING = True

    # Flask-SQLAlchemy overrides
    SQLALCHEMY_DATABASE_URI = 'postgres+psycopg2://light:devel@localhost:5432/lights'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Flask-DebugToolbar overrides
    DEBUG_TB_ENABLED = True
    DEBUG_TB_PROFILER_ENABLED = True
    # DEBUG_TB_INTERCEPT_REDIRECTS = True
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True


class TestingConfig(ProductionConfig):
    # Flask overrides
    TESTING = True

    # Flask-SQLAlchemy overrides
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # more explicit than 'sqlite://'

    # Flask + `unittest` module
    # This is required for `flask.url_for` to work as expected. Otherwise
    # it causes the function to raise errors and fails the tests because
    # it's unable to generate FQDNs for links.
    SERVER_NAME = 'localhost.test'


app_configs = {
    'development': 'app.config.DevelopmentConfig',
    'testing'    : 'app.config.TestingConfig',
    'production' : 'app.config.ProductionConfig',
}
