'''User service module to abstract the database ORM layer.

This module exposes functions for common User-oriented operations in
a way that avoids proliferating database-specific knowledge across the
rest of the system.
'''

# pylint: disable=no-member

from typing import List, Optional, Dict

from app.models import db
from app.models.user import User

from ._ops import (
    get_object_list,
    get_object,
    create_object,
    update_object,
    delete_object_list,
    delete_object
)


def get_user_list(**filters: Dict) -> List[User]:
    '''Get all `User` objects from the database, as a list.

    :param filters: A dictionary with model field/value pairs.

    :returns: A list of `User` objects.

    :raises InvalidPropertyError: One or more filters do not match model fields.
    '''
    return get_object_list(User, **filters)


def get_user(**filters: Dict) -> Optional[User]:
    '''Get the `User` specified by the given criteria.

    :param filters: A dictionary with model field/value pairs.

    :returns: A `User` object.

    :raises ObjectNotFoundError: A `User` with the given criteria was not found.

    :raises UniqueObjectExpectedError: The given criteria produced more than one `User`.

    :raises InvalidPropertyError: One or more filters do not exist as model field(s).
    '''
    return get_object(User, **filters)


def create_user(**data: Dict) -> Optional[User]:
    '''Create a new `User` from the diven data dictionary.

    :param data: A dictionary with key/value pairs that map to `User`
    field names and associated values.

    :raises DataIntegrityError: The dictionary data violates database
    integrity constraints.

    :raises ModelValidationError: The dictionary data violates validation rules.
    '''
    return create_object(User, **data)


def update_user(user: User) -> None:
    '''Update the specified `User`.

    :param user: The `User` to be updated.

    :raises DataIntegrityError: The `User` data violates database
    integrity constraints.

    :raises ModelValidationError: The dictionary data violates validation rules.

    :raises ObjectNotFoundError: The object to be updated does not exist.
    '''
    update_object(User, user)


def delete_user(user_id: int) -> None:
    '''Delete the `User` specified by the given ID.

    :param user_id: The database ID of the `User` to be deleted.
    '''
    delete_object(User, user_id)


def delete_user_list() -> None:
    '''Delete all the `User` objects from the database.'''
    delete_object_list(User)
