'''Light model unit tests module.'''
# pylint: disable=no-member
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

from typing import Callable
from datetime import (
    datetime as dt,
    timezone as tz
)

import pytest

from app import create_app
from app.settings import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH
)
from app.common.errors import ModelValidationError
from app.models import db
from app.models.light import Light

from tests.utils import (
    setup_database,
    teardown_database,
    setup_lights,
    teardown_lights,
    with_app_context
)


class TestLightModel:

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
        self.session = db.session   # pylint: disable=attribute-defined-outside-init

    def teardown_method(self, _method: Callable):
        teardown_lights(self.app)
        del self.app
        del self.session

    @with_app_context
    def test_light_creation_passes(self):
        Light(
            name='Bedroom',
            is_powered_on=True
        )

    @with_app_context
    def test_light_creation_without_data_raises_model_validation_error(self):
        with pytest.raises(ModelValidationError):
            self.session.add(Light())
            self.session.commit()

    @with_app_context
    def test_light_creation_without_name_raises_model_validation_error(self):
        with pytest.raises(ModelValidationError):
            self.session.add(Light(is_powered_on=True))
            self.session.commit()

    @with_app_context
    def test_light_creation_without_power_state_raises_model_validation_error(self):
        with pytest.raises(ModelValidationError):
            self.session.add(Light(name='Light-00'))
            self.session.commit()

    @with_app_context
    def test_light_name_below_min_length_raises_model_validation_error(self):
        light = Light.query.filter_by(id=1).one()
        with pytest.raises(ModelValidationError):
            light.name = 'a' * (MIN_NAME_LENGTH-1)

    @with_app_context
    def test_light_name_at_min_length_passes_validation(self):
        light = Light.query.filter_by(id=1).one()
        light.name = 'a' * MIN_NAME_LENGTH

    @with_app_context
    def test_light_name_above_max_length_raises_model_validation_error(self):
        light = Light.query.filter_by(id=1).one()
        with pytest.raises(ModelValidationError):
            light.name = 'a' * (MAX_NAME_LENGTH+1)

    @with_app_context
    def test_light_name_at_max_length_passes_validation(self):
        light = Light.query.filter_by(id=1).one()
        light.name = 'a' * MAX_NAME_LENGTH

    @with_app_context
    def test_light_power_state_truthy_values_pass(self):
        for index, state in enumerate((True, 'True', 'true', 't')):
            self.session.add(Light(
                name=f'Name-{index}',   # make names unique to avoid PK violations
                is_powered_on=state
            ))
            self.session.commit()

    @with_app_context
    def test_light_power_state_falsey_values_pass(self):
        for index, state in enumerate((False, 'False', 'false', 'f')):
            self.session.add(Light(
                name=f'Name-{index}',   # make names unique to avoid PK violations
                is_powered_on=state
            ))
            self.session.commit()

    @with_app_context
    def test_light_power_state_unexpected_value_raises_model_validation_error(self):
        values = ('T', '1', 'Yes', 'yes', 'Y', 'y', 'F', '0', 'No', 'no', 'N', 'n', None)
        with pytest.raises(ModelValidationError):
            for index, state in enumerate(values):
                self.session.add(Light(
                    name=f'Name-{index}',   # make names unique to avoid PK violations
                    is_powered_on=state
                ))
                self.session.commit()

    @with_app_context
    def test_date_created_field_format_matches(self):
        light = Light.query.filter_by(id=1).one()
        expected = dt.now(tz.utc).replace(microsecond=0)    # discard usecs; not stored in DB
        assert light.date_created == expected

    @with_app_context
    def test_light_repr_format_matches(self):
        light = Light.query.filter_by(id=1).one()
        actual = repr(light)
        expected = f"<Light: id={light.id} name='{light.name}' is_powered_on={light.is_powered_on}>"

        assert expected == actual
