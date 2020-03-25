'''The utilities module for the `tests` package.

This module has helper functions to make writing unit tests easier and
less verbose. Some of these functions include setup/teardown of in-memory
databases, tables, and test data.

This is a top-level module and functionality is expected to be common
across several testing sub-packages. All package-specific functionality
should be added within the nested/sub-package rather than this top-level
module. Said modules are also responsible for taking the proper
precautions for resetting their environments in-between unit tests.
'''

# pylint: disable=no-member

from typing import Text, Callable, Any
from functools import wraps

from flask import (
    url_for,
    Flask
)

from app.models import db
from app.models.light import Light
from app.models.user import User


def setup_database(app: Flask) -> None:
    '''Creates the database and all the tables in it.'''
    with app.app_context():
        db.create_all()


def teardown_database(app: Flask) -> None:
    '''Destroys the database and all the tables in it.'''
    with app.app_context():
        db.drop_all()


def setup_lights(app: Flask) -> None:
    '''Creates the `Light` data for unit tests.

    The table is created if it's not present. This is expected to
    happen in-between unit tests in order to reset the testing
    environment data and prevent side-effects from one unit test case
    from propagating to others and affecting their results.
    '''
    with app.app_context():
        # This check is needed because the first test always runs after
        # a `.create_all()` call, which would cause any attempts to re-
        # create existing tables to fail.
        engine = db.engine
        if not engine.dialect.has_table(engine, Light.__table__.name, Light.__table__.schema):
            Light.__table__.create(engine)

        for id in range(1, 4):
            db.session.add(Light(
                name=f'Light-{id}',
                is_powered_on=False
            ))
        db.session.commit()


def teardown_lights(app: Flask) -> None:
    '''Destroys the `Light` table to reset unit tests.

    The table is destroyed to remove changes that may've been introduced
    by unit tests and prevent them from propagating and affecting other
    unit tests.
    '''
    with app.app_context():
        Light.__table__.drop(db.engine)


def setup_users(app: Flask) -> None:
    '''Creates the `User` data for unit tests.

    The table is created if it's not present. This is expected to
    happen in-between unit tests in order to reset the testing
    environment data and prevent side-effects from one unit test case
    from propagating to others and affecting their results.
    '''
    with app.app_context():
        engine = db.engine
        if not engine.dialect.has_table(engine, User.__table__.name, User.__table__.schema):
            User.__table__.create(engine)

        for id in range(1, 3):
            db.session.add(User(
                name=f'User-{id}',
                password=f'User-App-Password-{id}'
            ))
        db.session.commit()


def teardown_users(app: Flask) -> None:
    '''Destroys the `User` table to reset unit tests.

    The table is destroyed to remove changes that may've been introduced
    by unit tests and prevent them from propagating and affecting other
    unit tests.
    '''
    with app.app_context():
        User.__table__.drop(db.engine)


def with_app_context(test_method: Callable[..., None]) -> Callable[..., None]:
    '''Run a test method within a `Flask.app_context`.

    :param `test_method`: A method with a `self` parameter, where
    `self.app` is a reference to the `Flask` object.

    When running unit tests for `Flask` apps, it's often necessary to
    perform database operations. These require an application context
    to be present, forcing all such cases to be explicitly written within
    the app's context manager. For example:

    ```
    def some_test(self, ...):
        with self.app.app_context():
            ...
    ```

    This is noisy and gets in the way of the actual tests you're trying
    to focus on. So, rather than doing that, use this decorator to solve
    the problem for you as it pushes/pops the correct app context manager
    for you automatically.

    If combined with methods using `hypothesis` decorators, this
    decorator *must* be the outter-most one to avoid errors due to how
    `hypothesis` handles function parameters. For example:

    ```
    # OK
    @with_app_context
    @given(...)
    def some_test(self, ...):
        ...
    ```

    rather than:

    ```
    # NOT OK
    @given(...)
    @with_app_context
    def some_test(self, ...):
        ...
    ```
    '''
    @wraps(test_method)
    def wrapper(self, *args, **kwargs) -> Any:
        with self.app.app_context():
            test_method(self, *args, **kwargs)

    return wrapper
