'''Internal module with model-specific utilities.

This module offers the recommended way to handle `DateTime` columns in
database tables. When defining the column, use the class(es) in this
module as shown in the example below:

    ```
    Column('timestamp', DateTime, server_default=utcnow())
    ```

For more information on why this is needed and/or recommended, see:
    https://docs.sqlalchemy.org/en/13/core/compiler.html#utc-timestamp-function
'''

# pylint: disable=no-member

from typing import Any

from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

from app.settings import TRUTHY, FALSEY


class utcnow(expression.FunctionElement):
    '''Guarantee SQL is emitted to store date/times in UTC.'''
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    # XXX: The time zone name must be lower-case and single-quoted.
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(utcnow, 'sqlite')
def sqlite_utcnow(element, compiler, **kw):
    return 'CURRENT_TIMESTAMP'


def try_to_bool(value: Any) -> bool:
    '''Try to convert a truthy or falsey value to a `bool` type.

    :param value: The value to be converted into a `bool` type.

    :returns: A `bool` type converted from the `value` or `None`
    to cause a `ValidationError`.

    Input data may've been received as a `bool` type from an internal
    call or as a `str` from a client request. The latter case may come
    from the `request.form`'s dictionary and is not auto-converted to
    `bool`. So we must handle this case by checking for `truthy` and
    `falsey` values we're reasonably willing to accept.

    Here we exclude `None` from `falsey` to raise `ValidationError`s
    when the data is actually missing; other falseys, such as empty
    lists/sets/tuples, we don't really care about here; client has a
    documented API spec to follow, so we're kind of being nice here.

    This function avoids applying the `bool(...)` function in order to
    prevent issues such as:
    ```
        >>> bool('False')
        True
    ```
    This function is intended to process "boolean" data sent by clients
    as JSON strings as well as the expected internal `bool` types.
    '''
    if value in TRUTHY:
        return True

    if value in FALSEY:
        return False

    return None
