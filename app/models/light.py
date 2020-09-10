'''The Light database model.

A model represents a database table with each instance being built from
each row. The instance fields are the database table columns.
'''

from typing import Text, Any
from datetime import (
    datetime,
    timezone
)

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    CheckConstraint
)
from sqlalchemy.orm import validates

from app.settings import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH,
    TRUTHY,
    FALSEY
)
from app.models import (
    db,
    _utils as utils
)
from app.common.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    ValueTypeValidator
)


class Light(db.Model):
    __tablename__ = 'light'
    __table_args__ = {'schema': 'public'}

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
    # This field must be overriden in the schema for serialization to
    # present it as a public field, without the `_` prefix.
    _is_powered_on = Column(
        'is_powered_on',
        Boolean,
        nullable=False
    )
    _date_created = Column(
        'date_created',
        DateTime,
        unique=False,
        nullable=False,
        server_default=utils.utcnow()   # not `datetime.utcnow`; see docs
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
        self._is_powered_on = utils.try_to_bool(value)

    @property
    def date_created(self) -> datetime:
        # The SQLA database migration is responsible for forcing the
        # database backend to emit SQL that guarantees the mapped column
        # is:
        #
        #   1. stored in a timezone-unaware format (i.e. a naive `datetime`);
        #   2. explicitly stored as UTC by the server backend.
        #
        # This is where the field's `utcnow` used above on `server_default`
        # comes in, which allows the `.replace` call below to work safely.
        return self._date_created.replace(tzinfo=timezone.utc)

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
