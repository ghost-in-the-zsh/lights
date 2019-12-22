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

from lights.settings import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH
)
from lights.models import db


class Light(db.Model):
    __tablename__ = 'light'

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

    def __repr__(self):
        return "<{}: id={} name='{}', is_powered_on={}>".format(
            self.__class__.__name__,
            self.id,
            self.name,
            str(self.is_powered_on)
        )
