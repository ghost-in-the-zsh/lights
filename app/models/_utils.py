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

from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime


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
