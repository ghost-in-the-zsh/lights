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

from lights.settings import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH
)
from lights.models import db
from lights.common.validators import (
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
