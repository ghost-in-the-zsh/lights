'''Light service unit tests module.'''
# pylint: disable=no-member
# pylint: disable=missing-function-docstring

from typing import Callable, Text

import pytest

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
from app.services.light import (
    get_light_list,
    create_light,
    get_light,
    update_light,
    delete_light,
    delete_light_list
)

from tests.utils import (
    setup_database,
    teardown_database,
    setup_lights,
    teardown_lights,
    with_app_context
)


class TestLightService:
    '''Unit tests for `services.light` functions.

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

    def setup_method(self, _method: Callable):
        app = self.__class__.app
        setup_lights(app)
        self.app = app

    def teardown_method(self, _method: Callable):
        teardown_lights(self.app)
        del self.app

    @with_app_context
    def test_get_light_list_is_ok(self):
        lights = get_light_list()
        assert len(lights) == 3

    @with_app_context
    def test_get_light_list_filtered_is_ok(self):
        lights = get_light_list(id=2)
        assert len(lights) == 1
        assert lights[0].id == 2

    @with_app_context
    def test_get_light_list_with_bad_filter_raises_invalid_property_error(self):
        with pytest.raises(InvalidPropertyError):
            get_light_list(kita='Baka')

    @with_app_context
    def test_get_light_id_is_ok(self, obj_id: int=1):
        light = get_light(id=obj_id)
        assert light.id == obj_id

    @with_app_context
    def test_nonexistent_positive_light_id_raises_object_not_found_error(self):
        with pytest.raises(ObjectNotFoundError):
            get_light(id=5)

    @with_app_context
    def test_nonexistent_negative_light_id_raises_object_not_found_error(self):
        with pytest.raises(ObjectNotFoundError):
            get_light(id=-1)

    @with_app_context
    def test_lax_search_criteria_raises_unique_object_expected_error(self):
        # Modify the in-memory database to make sure we can match several objects later
        for light in get_light_list():
            light.is_powered_on = False
            update_light(light)

        # This will now match more than a single light
        with pytest.raises(UniqueObjectExpectedError):
            get_light(is_powered_on=False)

    @with_app_context
    def test_update_light_is_ok(self, obj_id: int=1, name: Text='Living Room'):
        light = get_light(id=obj_id)
        light.name = name
        light.is_powered_on = False
        update_light(light)

        # trust, but verify
        light = get_light(id=obj_id)
        assert light.name == name
        assert light.is_powered_on is False

    @with_app_context
    def test_create_light_is_ok(self, name: Text='Restroom'):
        data = dict(name=name, is_powered_on=True)
        light = create_light(**data)

        assert light is not None
        assert light.id is not None and light.id > 0
        assert light.name == name
        assert light.is_powered_on is True

    @with_app_context
    def test_at_limit_min_length_light_name_creation_is_ok(self):
        data = dict(name='A'*MIN_NAME_LENGTH, is_powered_on=False)
        light = create_light(**data)
        assert light is not None

    @with_app_context
    def test_below_limit_min_length_name_light_creation_raises_model_validation_error(self):
        data = dict(name='A'*(MIN_NAME_LENGTH-1), is_powered_on=False)
        with pytest.raises(ModelValidationError):
            create_light(**data)

    @with_app_context
    def test_at_limit_max_length_name_light_name_creation_is_ok(self):
        data = dict(name='A'*MAX_NAME_LENGTH, is_powered_on=True)
        light = create_light(**data)
        assert light is not None

    @with_app_context
    def test_above_limit_max_length_name_light_creation_raises_model_validation_error(self):
        data = dict(name='A'*(MAX_NAME_LENGTH+1), is_powered_on=True)
        with pytest.raises(ModelValidationError):
            create_light(**data)

    @with_app_context
    def test_delete_existing_light_is_ok(self):
        delete_light(1)
        with pytest.raises(ObjectNotFoundError):
            get_light(id=1)

    @with_app_context
    def test_delete_non_existent_light_raises_object_not_found_error(self):
        with pytest.raises(ObjectNotFoundError):
            delete_light(10)

    @with_app_context
    def test_delete_collection_is_ok(self):
        delete_light_list()
