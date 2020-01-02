'''The Light database model.

A model represents a database table with each instance being built from
each row. The instance fields are the database table columns.
'''

from typing import Text, Any

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
    MaxLengthValidator,
    ValueTypeValidator
)


class Light(db.Model):
    __tablename__ = 'light'

    _validators = {
        'name': [
            MinLengthValidator(min_length=MIN_NAME_LENGTH),
            MaxLengthValidator(max_length=MAX_NAME_LENGTH),
        ],
        '_is_powered_on': [
            ValueTypeValidator(class_type=bool)
        ]
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
    _is_powered_on = Column(
        'is_powered_on',
        Boolean,
        nullable=False
    )

    def __init__(self, **kwargs):
        super()
        self.name = kwargs.get('name')
        self.is_powered_on = kwargs.get('is_powered_on')

    @property
    def is_powered_on(self) -> bool:
        return self._is_powered_on

    @is_powered_on.setter
    def is_powered_on(self, value: Any) -> None:
        self._is_powered_on = _try_to_bool(value)

    @validates('name')
    def _validate_name(self, field_name: Text, field_value: Text) -> Text:
        '''Validates the `name` field on assignment.

        :param field_name: The name of the field being validated.

        :param field_value: The value being assigned to the field.

        :raises ValidationError: The exception raised when value is rejected.
        '''
        return self._validate(field_name, field_value)

    @validates('_is_powered_on')
    def _validate_powerstate(self, field_name: Text, field_value: Any) -> Any:
        '''Validates the `_is_powered_on` field on assignment.

        :param field_name: The name of the field being validated.

        :param field_value: The value being assigned to the field.

        :raises ValidationError: The exception raised when value is rejected.
        '''
        return self._validate(field_name, field_value)

    def _validate(self, field_name: Text, field_value: Any) -> Any:
        '''Method with validation logic to dedup code.'''
        for validator in Light._validators[field_name]:
            validator.validate(field_value)
        return field_value

    def __repr__(self):
        return "<{}: id={} name='{}' is_powered_on={}>".format(
            self.__class__.__name__,
            self.id,
            self.name,
            self.is_powered_on
        )


def _try_to_bool(value: Any) -> bool:
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

        >>> bool('False')
        True

    This function is intended to process "boolean" data sent by clients
    as JSON strings as well as the expected internal `bool` types.
    '''
    if value in (True, 'True', 'true'):
        return True

    if value in (False, 'False', 'false'):
        return False

    return None
