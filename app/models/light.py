'''The Light database model.

A model represents a database table with each instance being built from
each row. The instance fields are the database table columns.
'''

from typing import Text

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    CheckConstraint
)
from sqlalchemy.orm import validates

from app.settings import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH
)
from app.models import db
from app.common.validators import (
    MinLengthValidator,
    MaxLengthValidator
)


class Light(db.Model):
    __tablename__ = 'light'

    _validators = {
        'name': [
            MinLengthValidator(min_length=MIN_NAME_LENGTH),
            MaxLengthValidator(max_length=MAX_NAME_LENGTH),
        ],
    }

    id = Column(
        Integer,
        primary_key=True
    )
    name = Column(
        String(MAX_NAME_LENGTH),
        CheckConstraint(f'length(name) >= {MIN_NAME_LENGTH} and length(name) <= {MAX_NAME_LENGTH}'),
        index=True,
        unique=True,
        nullable=False
    )
    is_powered_on = Column(
        Boolean,
        nullable=False
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = kwargs.get('name')

        # Input data may've been received as a `bool` type from an internal
        # call or as a `str` from a client request. The latter case comes
        # from the `request.form`'s dictionary and is not auto-converted to
        # `bool`. So we must handle this case by checking for `truthy` and
        # `falsey` values we're reasonably willing to accept.
        #
        # Here we exclude `None` from `falsey` to raise `ValidationError`s
        # when the data is actually missing; other falseys, such as empty
        # lists/sets/tuples, we don't really care about here; client has a
        # documented API spec to follow, so we're kind of being nice here.
        #
        # Avoid just doing `bool(value)` as that can bite you. For example,
        # a request with `{'is_powered_on': 'False'}` in the dictionary
        # evals to `True`, i.e. `bool('False') == True` is `True` (any non-
        # empty `str` is truthy), which is likely not what you want.
        is_powered_on = kwargs.get('is_powered_on')
        truthy = (True, 'True', 'true', 1)
        falsey = (False, 'False', 'false', 0, 0.0)
        if is_powered_on in truthy:
            self.is_powered_on = True
        elif is_powered_on in falsey:
            self.is_powered_on = False

    @validates('name')
    def _validate_name(self, column_name: Text, name_value: Text) -> Text:
        '''Validates the `name` field on assignment.

        :param column_name: The name of the field being validated.

        :param name_value: The value being assigned to the field.

        :raises ValidationError: The exception raised when value is rejected.
        '''
        for validator in Light._validators[column_name]:
            validator.validate(name_value)
        return name_value

    def __repr__(self):
        return "<{}: id={} name='{}' is_powered_on={}>".format(
            self.__class__.__name__,
            self.id,
            self.name,
            str(self.is_powered_on)
        )
