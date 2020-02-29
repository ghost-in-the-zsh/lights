'''The main lights application module.

This module creates and sets up the application to be run by the server.
'''

# pylint: disable=no-member

from typing import Text
from http import HTTPStatus

from flask import (
    Flask,
    current_app
)
from sqlalchemy import event
from sqlalchemy.engine import Engine

from flask_swagger_ui import get_swaggerui_blueprint as get_openapi_blueprint

from app.settings import (
    INSTANCE_DIR,
    DATABASE_SCHEMAS
)
from app.config import app_configs
from app.common.handlers import (
    http_400_handler,
    http_401_handler,
    http_403_handler,
    http_404_handler,
    http_405_handler,
    http_406_handler,
    http_500_handler,
    http_501_handler
)
from app.common.ext import moment
from app.common.filters import datetime_delta_filter
from app.debug import toolbar
from app.models import (
    db as sqla,
    migrate,
    marshmallow
)
from app.apis import current_api as api
from app.guis import (
    HomeView,
    LightView
)


def create_app(config_name: Text) -> Flask:
    # setup app
    app = Flask(__name__, instance_path=INSTANCE_DIR, template_folder='static/templates')
    app.config.from_object(app_configs[config_name])
    app.url_map.strict_slashes = False

    # init extensions
    sqla.init_app(app)
    migrate.init_app(app, sqla)
    marshmallow.init_app(app)   # must be init'ed *after* the SQLAlchemy ORM
    toolbar.init_app(app)
    moment.init_app(app)

    # register REST API
    prefix = f'/api/v{api.version}/lights'
    view_options = dict(trailing_slash=False, method_dashified=True)
    api.LightAPI.register(app, route_prefix=prefix, route_base='/', **view_options)

    # register GUI frontend
    HomeView.register(app, route_prefix='/', route_base='/', **view_options)
    LightView.register(app, route_prefix='/lights', route_base='/', **view_options)

    # register REST API docs
    prefix = '/api/docs'
    apibp = get_openapi_blueprint(
        prefix,
        f'/static/openapi-spec.json',
        config={'app_name': 'Lights'},
        blueprint_name='gui.home.apidocs'
    )
    app.register_blueprint(apibp, url_prefix=prefix)

    # register error handlers
    app.register_error_handler(HTTPStatus.BAD_REQUEST, http_400_handler)
    app.register_error_handler(HTTPStatus.UNAUTHORIZED, http_401_handler)
    app.register_error_handler(HTTPStatus.FORBIDDEN, http_403_handler)
    app.register_error_handler(HTTPStatus.NOT_FOUND, http_404_handler)
    app.register_error_handler(HTTPStatus.METHOD_NOT_ALLOWED, http_405_handler)
    app.register_error_handler(HTTPStatus.NOT_ACCEPTABLE, http_406_handler)
    app.register_error_handler(HTTPStatus.INTERNAL_SERVER_ERROR, http_500_handler)
    app.register_error_handler(HTTPStatus.NOT_IMPLEMENTED, http_501_handler)

    # add filters
    app.jinja_env.filters['datetime_delta'] = datetime_delta_filter

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

        # Postgres schemas (in the Postgres sense of the word) can be used
        # to organize database objects. The problem is that SQLite does
        # not support these kinds of schemas and Postgres cannot be run
        # as an in-memory database. (Well, maybe not easily.)
        #
        # This workaround takes the in-memory SQLite database and attaches
        # it as different SQLite schemas (in the SQLite sense) to allow
        # SQL queries to work in both database engines.
        #
        # This workaround only exists to allow local/automated unit tests
        # to work correctly, as SQLite gets confused otherwise (e.g. a
        # query for `<schema>.<table>` will fail b/c SQLite cannot find a
        # database[1] named `<schema>`).
        #
        # [1] For SQLite, a database is a schema; for Postgres a database
        #     *contains* one or more schemas.
        for pg_schema in DATABASE_SCHEMAS:
            cursor.execute(f'ATTACH DATABASE ":memory:" AS {pg_schema}')

        cursor.close()
