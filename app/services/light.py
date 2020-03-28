'''Light service module to abstract the database ORM layer.

This module exposes functions for common Light-oriented operations in
a way that avoids proliferating database-specific knowledge across the
rest of the system.
'''

# pylint: disable=no-member

from typing import List, Optional, Dict

from app.models import db
from app.models.light import Light

from ._ops import (
    get_object_list,
    get_object,
    create_object,
    update_object,
    delete_object_list,
    delete_object
)


def get_light_list(**filters: Dict) -> List[Light]:
    '''Get all `Light` objects from the database, as a list.

    :param filters: A dictionary with model field/value pairs.

    :returns: A list of `Light` objects.

    :raises InvalidPropertyError: One or more filters do not match model fields.
    '''
    _try_remap_fields(filters)
    return get_object_list(Light, **filters)


def get_light(**filters: Dict) -> Optional[Light]:
    '''Get the `Light` specified by the given criteria.

    :param filters: A dictionary with model field/value pairs.

    :returns: A `Light` object.

    :raises ObjectNotFoundError: A `Light` with the given criteria was not found.

    :raises UniqueObjectExpectedError: The given criteria produced more than one `Light`.

    :raises InvalidPropertyError: One or more filters do not exist as model field(s).
    '''
    _try_remap_fields(filters)
    return get_object(Light, **filters)


def create_light(**data: Dict) -> Optional[Light]:
    '''Create a new `Light` from the diven data dictionary.

    :param data: A dictionary with key/value pairs that map to `Light`
    field names and associated values.

    :raises DataIntegrityError: The dictionary data violates database
    integrity constraints.

    :raises ModelValidationError: The dictionary data violates validation rules.
    '''
    return create_object(Light, **data)


def update_light(light: Light) -> None:
    '''Update the specified `Light`.

    :param light: The `Light` to be updated.

    :raises DataIntegrityError: The `Light` data violates database
    integrity constraints.

    :raises ModelValidationError: The dictionary data violates validation rules.

    :raises ObjectNotFoundError: The object to be updated does not exist.
    '''
    update_object(Light, light)


def delete_light(light_id: int) -> None:
    '''Delete the `Light` specified by the given ID.

    :param light_id: The database ID of the `Light` to be deleted.
    '''
    delete_object(Light, light_id)


def delete_light_list() -> None:
    '''Delete all the `Light` objects from the database.'''
    delete_object_list(Light)


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
