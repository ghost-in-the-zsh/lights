'''Light service module to abstract the database ORM layer.

This module exposes functions for common Light-oriented operations in
a way that avoids proliferating database-specific knowledge across the
rest of the system.
'''

# pylint: disable=no-member

from typing import List, Optional, Dict

from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError
)
from sqlalchemy.orm.exc import NoResultFound

from app.common.errors import (
    ObjectNotFoundError,
    DataIntegrityError,
    InvalidPropertyError
)
from app.models import db
from app.models.light import Light


def get_light_list(filters: Dict=None) -> List[Light]:
    '''Get all `Light` objects from the database, as a list.

    :param filters: A dictionary with model field/value pairs.

    :returns: A list of `Light` objects.

    :raises InvalidPropertyError: One or more filters do not match model fields.
    '''
    if filters:
        try:
            return Light.query.filter_by(**filters).all()
        except InvalidRequestError as e:
            raise InvalidPropertyError(f'Filter(s) do not match model field(s): {filters}') from e

    return Light.query.all()


def get_light(light_id: int) -> Optional[Light]:
    '''Get the `Light` specified by the given ID.

    :param light_id: The database ID of the `Light` to search for.

    :returns: A `Light` object.

    :raises ObjectNotFoundError: A `Light` with the given :light_id: was not found.
    '''
    try:
        return Light.query.filter_by(id=light_id).one()
    except NoResultFound as e:
        raise ObjectNotFoundError(f'Light object {light_id} not found.') from e


def create_light(**data: Dict) -> Optional[Light]:
    '''Create a new `Light` from the diven data dictionary.

    :param data: A dictionary with key/value pairs that map to `Light`
    field names and associated values.

    :raises DataIntegrityError: The dictionary data violates database
    integrity constraints.

    :raises ValidationError: The dictionary data violates validation rules.
    '''
    light = Light(**data)
    session = db.session
    try:
        session.add(light)
        session.commit()
        return light
    except IntegrityError as e: # let client handle `ValidationError`
        session.rollback()
        raise DataIntegrityError(f'Light creation failed: {data}. {repr(e)}') from e


def update_light(light: Light) -> None:
    '''Update the specified `Light`.

    :param light: The `Light` to be updated.

    :raises DataIntegrityError: The `Light` data violates database
    integrity constraints.

    :raises ValidationError: The dictionary data violates validation rules.
    '''
    session = db.session
    try:
        session.add(light)
        session.commit()
    except IntegrityError as e: # let client handle `ValidationError`
        session.rollback()
        raise DataIntegrityError(f'Light {light.id} failed to update.') from e


def delete_light(light_id: int) -> None:
    '''Delete the `Light` specified by the given ID.

    :param light_id: The database ID of the `Light` to be deleted.
    '''
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