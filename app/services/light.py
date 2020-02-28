'''Light service module to abstract the database ORM layer.

This module exposes functions for common Light-oriented operations in
a way that avoids proliferating database-specific knowledge across the
rest of the system.
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
from app.models.light import Light


def get_light_list(**filters: Dict) -> List[Light]:
    '''Get all `Light` objects from the database, as a list.

    :param filters: A dictionary with model field/value pairs.

    :returns: A list of `Light` objects.

    :raises InvalidPropertyError: One or more filters do not match model fields.
    '''
    if not filters:
        return Light.query.all()

    _try_remap_fields(filters)
    try:
        return Light.query.filter_by(**filters).all()
    except InvalidRequestError as e:
        raise InvalidPropertyError(f'Filter(s) do(es) not match model field(s): {filters}') from e


def get_light(**filters: Dict) -> Optional[Light]:
    '''Get the `Light` specified by the given criteria.

    :param filters: A dictionary with model field/value pairs.

    :returns: A `Light` object.

    :raises ObjectNotFoundError: A `Light` with the given criteria was not found.

    :raises UniqueObjectExpectedError: The given criteria produced more than one `Light`.

    :raises InvalidPropertyError: One or more filters do not exist as model field(s).
    '''
    _try_remap_fields(filters)
    try:
        return Light.query.filter_by(**filters).one()
    except NoResultFound as e:
        raise ObjectNotFoundError(f'Light not found: {filters}') from e
    except MultipleResultsFound as e:
        raise UniqueObjectExpectedError(f'More than one Light found. Use more specific criteria: {filters}') from e
    except InvalidRequestError as e:
        raise InvalidPropertyError(f'Light filter(s) and model field(s) mismatch: {filters}') from e


def create_light(**data: Dict) -> Optional[Light]:
    '''Create a new `Light` from the diven data dictionary.

    :param data: A dictionary with key/value pairs that map to `Light`
    field names and associated values.

    :raises DataIntegrityError: The dictionary data violates database
    integrity constraints.

    :raises ModelValidationError: The dictionary data violates validation rules.
    '''
    light = Light(**data)
    session = db.session
    try:
        session.add(light)
        session.commit()
        return light
    except (IntegrityError, StatementError) as e: # let caller handle `ModelValidationError`
        session.rollback()
        raise DataIntegrityError(f'Light creation failed: {data}. {repr(e)}') from e


def update_light(light: Light) -> None:
    '''Update the specified `Light`.

    :param light: The `Light` to be updated.

    :raises DataIntegrityError: The `Light` data violates database
    integrity constraints.

    :raises ModelValidationError: The dictionary data violates validation rules.

    :raises ObjectNotFoundError: The object to be updated does not exist.
    '''
    session = db.session
    try:
        session.add(light)
        session.commit()
    except (IntegrityError, StatementError) as e: # let caller handle `ModelValidationError`
        session.rollback()
        raise DataIntegrityError(f'Light {light.id} failed to update.') from e


def delete_light(light_id: int) -> None:
    '''Delete the `Light` specified by the given ID.

    :param light_id: The database ID of the `Light` to be deleted.
    '''
    if not _light_exists(light_id):
        raise ObjectNotFoundError(f'Light object {light_id} not found.')

    session = db.session
    try:
        Light.query.filter_by(id=light_id).delete()
        session.commit()
    except IntegrityError as e:
        # This is included for the sake of completeness; the `light` table
        # has no other defined relations or constraints (e.g. foreign keys),
        # so deleting a `Light` does not raise exceptions in our case.
        session.rollback()
        raise DataIntegrityError(f'Light {light_id} cannot be deleted.') from e


def delete_light_list() -> None:
    '''Delete all the `Light` objects from the database.'''
    # The docs[1] don't list errors raised by this implementation,
    # so it's probably like `delete_light`'s implementation.
    # See docs for caveats.
    #
    # [1] https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query.delete
    session = db.session
    try:
        Light.query.delete(synchronize_session=False)
        session.commit()
    except IntegrityError as e:
        # See notes in `delete_light`
        session.rollback()
        raise DataIntegrityError(f'Lights collection could not be deleted') from e


def _light_exists(light_id: int) -> bool:
    '''Return `True` if the `Light` exists. Otherwise `False`.

    This is a less expensive way of checking for its existence, as it only
    gets the scalar `Light.id` field instead of loading and instantiating a
    full object just to throw it away.
    '''
    session = db.session
    return session.query(Light.id).filter_by(id=light_id).scalar() is not None


def _try_remap_fields(filters: Dict) -> None:
    '''Map public-facing field names to private field names.

    When the `services` module is being used and filters/kwargs passed
    in, it's the public field names that are expected to be used. However,
    this causes searches to fail on the query b/c those work with the
    Python-defined `Column` fields, but some of those fields are protected
    by property methods.

    For the search to work correctly, we re-assign the public field name
    to the private instance field name when necessary.
    '''
    # XXX: Is there a better way to handle this so that no
    # remapping is needed?
    if 'is_powered_on' in filters:
        filters['_is_powered_on'] = filters['is_powered_on']
        del filters['is_powered_on']
