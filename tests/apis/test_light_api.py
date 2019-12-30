'''The Light API test module.

Note that the naming convention in this module (e.g. for classes,
module names, etc) is as it is so that `pytest` can find them via
introspection.
'''

# pylint: disable=no-member

from typing import (
    Callable,
    Dict
)
from http import HTTPStatus

from flask import url_for

from app import create_app
from app.settings import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH
)
from app.apis import current_api
from app.models import db
from app.models.light import Light

from tests.utils import (
    setup_database,
    teardown_database,
    setup_lights,
    teardown_lights,
    with_app_context
)


class TestLightGetAPI(object):
    '''Unit tests for the `GET` methods of the `LightAPI` class.'''

    @classmethod
    def setup_class(cls):
        app = create_app('testing')
        setup_database(app)
        cls.app = app

    @classmethod
    def teardown_class(cls):
        teardown_database(cls.app)
        del cls.app

    def setup_method(self, method: Callable):
        app = self.__class__.app
        client = app.test_client()
        setup_lights(app)

        self.app = app
        self.client = client
        self.api_ver = current_api.version
        self.mime_type = 'application/json'

    def teardown_method(self, method: Callable):
        teardown_lights(self.app)
        del self.client
        del self.app

    @with_app_context
    def test_light_list_request_is_ok(self):
        url = url_for(f'api.v{self.api_ver}.light.get_all')
        total = db.session.query(Light).count()
        expected = {
            '_meta': {
                'stats': {
                    'total_count': total
                },
                'links': [{
                    'rel': 'self',
                    'href': url_for(f'api.v{self.api_ver}.light.get_all')
                }]
            },
            'lights': [
                {
                    '_meta': {
                        'links': [
                            {
                                'rel': 'self',
                                'href': url_for(f'api.v{self.api_ver}.light.detail', id=id)
                            }
                        ]
                    },
                    'id': id,
                    'name': f'Light-{id}',
                    'is_powered_on': False
                } for id in range(1, total+1)
            ]
        }
        response = self.client.get(url, content_type=self.mime_type)
        actual = response.json

        assert response.status_code == HTTPStatus.OK.value
        assert response.content_type == self.mime_type
        assert expected == actual

    @with_app_context
    def test_light_request_by_id_is_ok(self, id: int=1):
        url = url_for(f'api.v{self.api_ver}.light.detail', id=id)
        expected = {
            'light': {
                '_meta': {
                    'links': [
                        {
                            'rel': 'self',
                            'href': url_for(f'api.v{self.api_ver}.light.detail', id=id)
                        }
                    ]
                },
                'id': id,
                'name': f'Light-{id}',
                'is_powered_on': False
            }
        }
        response = self.client.get(url, content_type=self.mime_type)
        actual = response.json

        assert response.status_code == HTTPStatus.OK.value
        assert response.content_type == self.mime_type
        assert expected == actual

    @with_app_context
    def test_light_request_by_non_existent_positive_id_is_not_found(self):
        url = url_for(f'api.v{self.api_ver}.light.detail', id=10)
        response = self.client.get(url, content_type=self.mime_type)

        assert response.status_code == HTTPStatus.NOT_FOUND.value
        assert response.content_type == self.mime_type

    @with_app_context
    def test_light_request_by_non_existent_negative_id_is_not_found(self):
        url = url_for(f'api.v{self.api_ver}.light.detail', id=-5)
        response = self.client.get(url, content_type=self.mime_type)

        assert response.status_code == HTTPStatus.NOT_FOUND.value
        assert response.content_type == self.mime_type
