'''Light model unit tests module.'''
# pylint: disable=no-member

import pytest

from typing import Callable, Dict, Text

from sqlalchemy.exc import IntegrityError

from lights import create_app
from lights.models import db
from lights.models.light import Light

from tests.utils import (
    setup_database,
    teardown_database,
    setup_lights,
    teardown_lights,
    with_app_context
)


class TestLightModel(object):

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
        setup_lights(app)
        self.app = app
        self.session = db.session

    def teardown_method(self, method: Callable):
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
    def test_light_creation_without_data_raises_integrity_error(self):
        with pytest.raises(IntegrityError):
            self.session.add(Light())
            self.session.commit()

    @with_app_context
    def test_light_creation_without_name_raises_integrity_error(self):
        with pytest.raises(IntegrityError):
            self.session.add(Light(is_powered_on=True))
            self.session.commit()

    @with_app_context
    def test_light_creation_without_power_state_raises_integrity_error(self):
        with pytest.raises(IntegrityError):
            self.session.add(Light(name='Light-00'))
            self.session.commit()
