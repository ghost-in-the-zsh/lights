# pylint: disable=no-member

import pytest
from pytest import mark

from typing import Callable, Dict, Text

from app import create_app
from app.settings import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH
)
from app.common.errors import (
    ObjectNotFoundError,
    InvalidPropertyError,
    ModelValidationError,
    UniqueObjectExpectedError
)
from app.services.user import (
    get_user_list,
    create_user,
    get_user,
    update_user,
    delete_user,
    delete_user_list
)

from tests.utils import (
    setup_database,
    teardown_database,
    setup_users,
    teardown_users,
    with_app_context
)


# If you get sudden failures, then this password was likely/somehow found
# in a known breach. Just change it to something else that allows the
# tests to pass.
#
# The `User` class has a `PasswordBreachValidator` class that verifies
# this and it should not be disabled.
DEFAULT_PASSWORD = 'This should pass the breach validator'


class TestUserService(object):
    '''Unit tests for `services.user` functions.

    Test cases for raising `DataIntegrityError` are not included because
    the field validators take effect before the data ever makes it into the
    the database backend, raising `ModelValidationError` instead.
    '''

    @classmethod
    def setup_class(cls):
        app = create_app('testing')
        setup_database(app)
        cls.app = app

    @classmethod
    def teardown_class(cls):
        teardown_database(cls.app)

    def setup_method(self, method: Callable):
        app = self.__class__.app
        setup_users(app)
        self.app = app

    def teardown_method(self, method: Callable):
        teardown_users(self.app)
        del self.app

    @with_app_context
    def test_get_user_list_is_ok(self):
        users = get_user_list()
        assert len(users) == 2

    @with_app_context
    def test_get_user_list_filtered_is_ok(self):
        users = get_user_list(id=2)
        assert len(users) == 1
        assert users[0].id == 2

    @with_app_context
    def test_get_user_list_with_bad_filter_raises_invalid_property_error(self):
        with pytest.raises(InvalidPropertyError):
            get_user_list(kita='Baka')

    @with_app_context
    def test_get_user_id_is_ok(self, id: int=1):
        user = get_user(id=id)
        assert user.id == id

    @with_app_context
    def test_nonexistent_positive_user_id_raises_object_not_found_error(self):
        with pytest.raises(ObjectNotFoundError):
            get_user(id=5)

    @with_app_context
    def test_nonexistent_negative_user_id_raises_object_not_found_error(self):
        with pytest.raises(ObjectNotFoundError):
            get_user(id=-1)

    @with_app_context
    @mark.skip(reason='Current fields cannot be used for this test case')
    def test_lax_search_criteria_raises_unique_object_expected_error(self):
        # This case cannot be exec'd at this time. Reasons are:
        #   1. User.name field is set to be unique, so cannot be duplicated.
        #   2. User.password field is hashed in such a way that even duplicate
        #      passwords produce different hashes.
        # If new fields that can be used for this get added, then this case
        # can be revisited.
        pass

    @with_app_context
    def test_update_user_is_ok(self, id: int=1, name: Text='User-15', password: Text=DEFAULT_PASSWORD):
        user = get_user(id=id)
        old_hash = user.password_hash
        user.name = name
        user.password = password
        update_user(user)

        # trust, but verify
        user = get_user(id=id)
        assert user.name == name
        assert user.password_hash != old_hash

    @with_app_context
    def test_create_user_is_ok(self, name: Text='User-99'):
        data = dict(name=name, password=DEFAULT_PASSWORD)
        user = create_user(**data)

        assert user != None
        assert user.id != None and user.id > 0
        assert user.name == name
        assert user.password_hash is not None

    @with_app_context
    def test_at_limit_min_length_user_name_creation_is_ok(self):
        data = dict(name='A'*MIN_NAME_LENGTH, password=DEFAULT_PASSWORD)
        user = create_user(**data)
        assert user != None

    @with_app_context
    def test_below_limit_min_length_name_user_creation_raises_model_validation_error(self):
        data = dict(name='A'*(MIN_NAME_LENGTH-1), password=DEFAULT_PASSWORD)
        with pytest.raises(ModelValidationError):
            create_user(**data)

    @with_app_context
    def test_at_limit_max_length_name_user_name_creation_is_ok(self):
        data = dict(name='A'*MAX_NAME_LENGTH, password=DEFAULT_PASSWORD)
        user = create_user(**data)
        assert user != None

    @with_app_context
    def test_above_limit_max_length_name_user_creation_raises_model_validation_error(self):
        data = dict(name='A'*(MAX_NAME_LENGTH+1), password=DEFAULT_PASSWORD)
        with pytest.raises(ModelValidationError):
            create_user(**data)

    @with_app_context
    def test_delete_existing_user_is_ok(self):
        delete_user(1)
        with pytest.raises(ObjectNotFoundError):
            get_user(id=1)

    @with_app_context
    def test_delete_non_existent_user_raises_object_not_found_error(self):
        with pytest.raises(ObjectNotFoundError):
            delete_user(10)

    @with_app_context
    def test_delete_collection_is_ok(self):
        delete_user_list()
