'''The main lights application module.

This module creates and sets up the application to be run by the server.
'''

# pylint: disable=no-member

from typing import Text

from flask import (
    Flask,
    current_app
)
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.settings import INSTANCE_DIR
from app.config import app_configs
from app.models import (
    db as sqla,
    migrate,
)


def create_app(config_name: Text) -> Flask:
    # setup app
    app = Flask(__name__, instance_path=INSTANCE_DIR)
    app.config.from_object(app_configs[config_name])

    # init extensions
    sqla.init_app(app)
    migrate.init_app(app, sqla)

    return app


@event.listens_for(Engine, 'connect')
def _on_database_connected(dbapi_connection, connection_record):
    '''Event handler for when a connection to the DB is made.

    The standard built-in SQLite3 DB is used for local development and/or
    testing only. Unfortunately, foreign key support is *still disabled*
    by default[1], which causes the DB to ignore defined constraints
    such as `on {delete | update} cascade`, leaving orphaned child rows
    and causing data integrity issues, false test failures, etc.

    This must be enabled *on each connection* to the DB so that it works
    correctly and in the same way the non-SQLite production environment
    is expected to work.

    The SQL statement may be considered illegal syntax and fail with an
    exception (e.g. on Postgres). Therefore, the implementation checks if
    the database dialect is `sqlite` before trying to run the statement.

    There're some reasons for why this is not using a try/except block:

        1. Exception matching/handling costs add up for many connections;
        2. Backend libraries raise different exceptions (i.e. can miss);
        3. Even when catching `Exception`, containers could fail to run;
        4. I'm not aware of a more elegant way to do this (yet?);

    On #4, I'm not aware of a way to register an event listener that fires
    when connecting to a SQLite-backed database *only*. For now, it's an
    all-or-nothing proposition.

    This particular project doesn't really benefit from this, but now you
    know the catch before it catches you. You're welcome ;)

    [1] "Enabling Foreign Key Support", https://sqlite.org/foreignkeys.html
    '''
    if 'sqlite' in current_app.config['SQLALCHEMY_DATABASE_URI']:
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys = on')
        cursor.close()
