'''Configuration module for Flask application objects.

The configuration classes describe the properties that should be applied
to Flask application instances, based on their execution environment.
'''

from app.settings import (
    VERSION,
    INSTANCE_DIR,
    DATABASE_CONFIG
)


class ProductionConfig:
    VERSION = VERSION

    # Flask
    # http://flask.palletsprojects.com/en/1.1.x/config/
    DEBUG = False
    TESTING = False

    # Flask-SQLAlchemy
    # https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
    # https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls
    SQLALCHEMY_DATABASE_URI = '%(dialect)s+%(driver)s://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s' % DATABASE_CONFIG
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(ProductionConfig):
    # Flask overrides
    DEBUG = True
    EXPLAIN_TEMPLATE_LOADING = True

    # Flask-SQLAlchemy overrides
    SQLALCHEMY_DATABASE_URI = 'postgres+psycopg2://lights:devel@localhost:5432/lights'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


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
