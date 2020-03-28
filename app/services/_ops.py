'''Private CRUD ops service module to abstract the database ORM layer.

This private module has functions for common CRUD operations in a way
that avoids proliferating database-specific knowledge across the rest of
the system. This module is intended for use only by other `service`
package modules.
'''

# pylint: disable=no-member

from typing import List, Optional, Dict

from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    StatementError
)
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound
)

from app.common.errors import (
    ObjectNotFoundError,
    DataIntegrityError,
    InvalidPropertyError,
    UniqueObjectExpectedError
)
from app.models import db


def get_object_list(cls: db.Model, **filters: Dict) -> List[db.Model]:
    '''Get all `cls` objects from the database, as a list.

    :param cls: The model class of the objects to fetch.

    :param filters: A dictionary with model field/value pairs.

    :returns: A list of `cls` objects.

    :raises InvalidPropertyError: One or more filters do not match model fields.
    '''
    if not filters:
        return cls.query.all()

    try:
        return cls.query.filter_by(**filters).all()
    except InvalidRequestError as e:
        raise InvalidPropertyError(f'Filter(s) do(es) not match model field(s): {filters}') from e


def get_object(cls: db.Model, **filters: Dict) -> Optional[db.Model]:
    '''Get the `cls` object specified by the given criteria.

    :param cls: The model class of the objects to fetch.

    :param filters: A dictionary with model field/value pairs.

    :returns: A `cls` object.

    :raises ObjectNotFoundError: A `cls` with the given criteria was not found.

    :raises UniqueObjectExpectedError: The criteria found more than one `cls`.

    :raises InvalidPropertyError: One or more filters do not exist as model field(s).
    '''
    try:
        return cls.query.filter_by(**filters).one()
    except NoResultFound as e:
        raise ObjectNotFoundError(f'{cls.__name__} not found: {filters}') from e
    except MultipleResultsFound as e:
        raise UniqueObjectExpectedError(f'More than one {cls.__name__} found. Use more specific criteria: {filters}') from e
    except InvalidRequestError as e:
        raise InvalidPropertyError(f'{cls.__name__} filter(s) and model field(s) mismatch: {filters}') from e


def create_object(cls: db.Model, **data: Dict) -> Optional[db.Model]:
    '''Create a new `cls` from the diven data dictionary.

    :param cls: The model class of the objects to create.

    :param data: A dictionary with key/value pairs that map to `cls`
    field names and associated values.

    :raises DataIntegrityError: The dictionary data violates database
    integrity constraints.

    :raises ModelValidationError: The dictionary data violates validation rules.
    '''
    obj = cls(**data)
    session = db.session
    try:
        session.add(obj)
        session.commit()
        return obj
    except (IntegrityError, StatementError) as e: # let caller handle `ModelValidationError`
        session.rollback()
        raise DataIntegrityError(f'{cls.__name__} creation failed: {data}. {repr(e)}') from e


def update_object(cls: db.Model, obj: db.Model) -> None:
    '''Update the specified `cls`.

    :param cls: The model class of the objects to update.

    :param obj: The `cls` to be updated.

    :raises DataIntegrityError: The `cls` data violates database
    integrity constraints.

    :raises ModelValidationError: The dictionary data violates validation rules.

    :raises ObjectNotFoundError: The object to be updated does not exist.
    '''
    session = db.session
    try:
        session.add(obj)
        session.commit()
    except (IntegrityError, StatementError) as e: # let caller handle `ModelValidationError`
        session.rollback()
        raise DataIntegrityError(f'{cls.__name__} {obj.id} failed to update.') from e


def delete_object(cls: db.Model, obj_id: int) -> None:
    '''Delete the instance specified by the given ID.

    :param cls: The model class of the objects to delete.

    :param obj_id: The database ID of the instance to be deleted.
    '''
    if not _object_exists(cls, obj_id):
        raise ObjectNotFoundError(f'{cls.__name__} object {obj_id} not found.')

    session = db.session
    try:
        cls.query.filter_by(id=obj_id).delete()
        session.commit()
    except IntegrityError as e:
        # This is included for the sake of completeness; the model tables
        # have no other defined relations or constraints (e.g. foreign keys),
        # so deleting an object does not raise exceptions in our case.
        session.rollback()
        raise DataIntegrityError(f'{cls.__name__} {obj_id} cannot be deleted.') from e


def delete_object_list(cls: db.Model) -> None:
    '''Delete all the `cls` objects from the database.

    :param cls: The model class of the objects to delete.
    '''
    # The docs[1] don't list errors raised by this implementation,
    # so it's probably like `delete_object`'s implementation.
    # See docs for caveats.
    #
    # [1] https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query.delete
    session = db.session
    try:
        cls.query.delete(synchronize_session=False)
        session.commit()
    except IntegrityError as e:
        # See notes in `delete_object`
        session.rollback()
        raise DataIntegrityError(f'{cls.__name__}s collection could not be deleted') from e


def _object_exists(cls: db.Model, obj_id: int) -> bool:
    '''Return `True` if the `cls` instance exists. Otherwise `False`.

    This is a less expensive way of checking for its existence, as it only
    gets the scalar `cls.id` field instead of loading and instantiating a
    full object just to throw it away.
    '''
    session = db.session
    return session.query(cls.id).filter_by(id=obj_id).scalar() is not None
