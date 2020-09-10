'''The Light API test module.

Note that the naming convention in this module (e.g. for classes,
module names, etc) is as it is so that `pytest` can find them via
introspection.
'''

# pylint: disable=no-member

import json

from typing import (
    Callable,
    Dict
)
from datetime import (
    datetime as dt,
    timezone as tz
)
from http import HTTPStatus

from flask import url_for
from pytest import mark

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


BASE_URL = f'api.v{current_api.version}.light'
MIME_TYPE = 'application/json'


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

    def teardown_method(self, method: Callable):
        teardown_lights(self.app)
        del self.client
        del self.app

    @with_app_context
    def test_light_list_request_is_ok(self):
        url = url_for(f'{BASE_URL}.get_all')
        total = db.session.query(Light).count()
        expected = {
            '_meta': {
                'stats': {
                    'total_count': total
                },
                'links': [{
                    'rel': 'self',
                    'href': url_for(f'{BASE_URL}.get_all')
                }]
            },
            'lights': [
                {
                    '_meta': {
                        'links': [
                            {
                                'rel': 'self',
                                'href': url_for(f'{BASE_URL}.detail', id=id)
                            }
                        ]
                    },
                    'id': id,
                    'name': f'Light-{id}',
                    'is_powered_on': False,
                    'date_created': dt.now(tz.utc).isoformat(timespec='seconds')
                } for id in range(1, total+1)
            ]
        }
        response = self.client.get(
            url,
            headers={'Accept': MIME_TYPE}
        )
        actual = response.json

        assert response.status_code == HTTPStatus.OK.value
        assert response.content_type == MIME_TYPE
        assert expected == actual

    @with_app_context
    def test_light_request_by_id_is_ok(self, id: int=1):
        url = url_for(f'{BASE_URL}.detail', id=id)
        expected = {
            'light': {
                '_meta': {
                    'links': [
                        {
                            'rel': 'self',
                            'href': url_for(f'{BASE_URL}.detail', id=id)
                        }
                    ]
                },
                'id': id,
                'name': f'Light-{id}',
                'is_powered_on': False,
                'date_created': dt.now(tz.utc).isoformat(timespec='seconds')
            }
        }
        response = self.client.get(
            url,
            headers={'Accept': MIME_TYPE}
        )
        actual = response.json

        assert response.status_code == HTTPStatus.OK.value
        assert response.content_type == MIME_TYPE
        assert expected == actual

    @with_app_context
    def test_light_request_by_non_existent_positive_id_is_not_found(self):
        url = url_for(f'{BASE_URL}.detail', id=10)
        response = self.client.get(
            url,
            headers={'Accept': MIME_TYPE}
        )

        assert response.status_code == HTTPStatus.NOT_FOUND.value
        assert response.content_type == MIME_TYPE

    @with_app_context
    def test_light_request_by_non_existent_negative_id_is_not_found(self):
        url = url_for(f'{BASE_URL}.detail', id=-5)
        response = self.client.get(
            url,
            headers={'Accept': MIME_TYPE}
        )

        assert response.status_code == HTTPStatus.NOT_FOUND.value
        assert response.content_type == MIME_TYPE


class TestLightPostAPI(object):
    '''Unit tests for the `POST` methods of the `LightAPI` class.'''

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

    def teardown_method(self, method: Callable):
        teardown_lights(self.app)
        del self.client
        del self.app

    @with_app_context
    def test_valid_request_is_created(self):
        data = dict(
            name='A Valid Name',
            is_powered_on=False     # prevent `bool('False') == True` on the server-side
        )
        root_url = url_for(f'{BASE_URL}.submit_new')

        response = self.client.post(
            root_url,
            data=json.dumps(data),
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE
            }
        )

        actual = response.json
        self_url = url_for(f'{BASE_URL}.detail', id=actual['light']['id'])
        expected = {
            'light': {
                'id': actual['light']['id'],
                'name': data['name'],
                'is_powered_on': data['is_powered_on'],
                'date_created': dt.now(tz.utc).isoformat(timespec='seconds')
            }
        }

        assert response.status_code == HTTPStatus.CREATED.value
        assert response.content_type == MIME_TYPE
        assert response.headers['Location'] == self_url
        assert expected == actual

    @with_app_context
    def test_request_with_invalid_short_name_is_bad_request(self):
        data = dict(
            name='A'*(MIN_NAME_LENGTH-1),
            is_powered_on=False
        )
        root_url = url_for(f'{BASE_URL}.submit_new')
        response = self.client.post(
            root_url,
            data=data,
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE
            }
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST.value
        assert response.content_type == MIME_TYPE

    @with_app_context
    def test_request_with_invalid_long_name_is_bad_request(self):
        data = dict(
            name='A'*(MAX_NAME_LENGTH+1),
            is_powered_on=False
        )
        root_url = url_for(f'{BASE_URL}.submit_new')
        response = self.client.post(
            root_url,
            data=data,
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE
            }
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST.value
        assert response.content_type == MIME_TYPE


class TestLightPutAPI(object):
    '''Unit tests for the `PUT` methods of the `LightAPI` class.'''

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

    def teardown_method(self, method: Callable):
        teardown_lights(self.app)
        del self.client
        del self.app

    @with_app_context
    def test_put_request_returns_no_content(self, id: int=1, name: str='New Name', power_state: bool=True):
        root_url = url_for(f'{BASE_URL}.replace', id=id)
        response = self.client.put(
            root_url,
            data=json.dumps(dict(
                name=name,
                is_powered_on=power_state
            )),
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE
            }
        )

        assert response.status_code == HTTPStatus.NO_CONTENT.value
        assert response.content_type == MIME_TYPE

        # verify the resource actually changed with a `GET` request
        url = url_for(f'{BASE_URL}.detail', id=id)
        expected = {
            'light': {
                '_meta': {
                    'links': [
                        {
                            'rel': 'self',
                            'href': url_for(f'{BASE_URL}.detail', id=id)
                        }
                    ]
                },
                'id': id,
                'name': name,
                'is_powered_on': power_state,
                'date_created': dt.now(tz.utc).isoformat(timespec='seconds')
            }
        }
        response = self.client.get(url, content_type=MIME_TYPE)
        actual = response.json

        assert response.status_code == HTTPStatus.OK.value
        assert response.content_type == MIME_TYPE
        assert expected == actual

    @with_app_context
    def test_put_request_on_non_existent_id_is_not_found(self, id: int=15):
        root_url = url_for(f'{BASE_URL}.replace', id=id)
        response = self.client.put(
            root_url,
            data=dict(
                name='Wowee',
                is_powered_on=True
            ),
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE
            }
        )

        assert response.status_code == HTTPStatus.NOT_FOUND.value
        assert response.content_type == MIME_TYPE

    @with_app_context
    def test_put_request_with_no_data_is_bad_request(self, id: int=1):
        root_url = url_for(f'{BASE_URL}.replace', id=id)
        response = self.client.put(
            root_url,
            data=None,
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE
            }
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST.value
        assert response.content_type == MIME_TYPE


class TestLightPatchAPI(object):
    '''Unit tests for the `PATCH` methods of the `LightAPI` class.'''

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

    def teardown_method(self, method: Callable):
        teardown_lights(self.app)
        del self.client
        del self.app

    @with_app_context
    @mark.skip(reason='Standard-compliant implementation and test audit not complete.')
    def test_patch_request_to_update_name_returns_no_content(self, id: int=1, name: str='New Name'):
        root_url = url_for(f'{BASE_URL}.update', id=id)
        response = self.client.patch(
            root_url,
            data=dict(name=name),
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE
            }
        )

        assert response.status_code == HTTPStatus.NO_CONTENT.value
        assert response.content_type == MIME_TYPE

        # verify the resource actually changed with a `GET` request
        url = url_for(f'{BASE_URL}.detail', id=id)
        expected = {
            'light': {
                '_meta': {
                    'links': [
                        {
                            'rel': 'self',
                            'href': url_for(f'{BASE_URL}.detail', id=id)
                        }
                    ]
                },
                'id': id,
                'name': name,
                'is_powered_on': False
            }
        }
        response = self.client.get(url, content_type=MIME_TYPE)
        actual = response.json

        assert response.status_code == HTTPStatus.OK.value
        assert response.content_type == MIME_TYPE
        assert expected == actual

    @with_app_context
    @mark.skip(reason='Standard-compliant implementation and test audit not complete.')
    def test_patch_request_to_update_power_state_returns_no_content(self, id: int=1, power_state: bool=True):
        root_url = url_for(f'{BASE_URL}.update', id=id)
        response = self.client.patch(
            root_url,
            data=dict(is_powered_on=power_state),
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE
            }
        )

        assert response.status_code == HTTPStatus.NO_CONTENT.value
        assert response.content_type == MIME_TYPE

        # verify the resource actually changed with a `GET` request
        url = url_for(f'{BASE_URL}.detail', id=id)
        expected = {
            'light': {
                '_meta': {
                    'links': [
                        {
                            'rel': 'self',
                            'href': url_for(f'{BASE_URL}.detail', id=id)
                        }
                    ]
                },
                'id': id,
                'name': f'Light-{id}',
                'is_powered_on': power_state
            }
        }
        response = self.client.get(url, content_type=MIME_TYPE)
        actual = response.json

        assert response.status_code == HTTPStatus.OK.value
        assert response.content_type == MIME_TYPE
        assert expected == actual

    @with_app_context
    @mark.skip(reason='Standard-compliant implementation and test audit not complete.')
    def test_patch_request_on_non_existent_id_is_not_found(self, id: int=15):
        root_url = url_for(f'{BASE_URL}.update', id=id)
        response = self.client.patch(
            root_url,
            data=dict(
                name='Wowee',
                is_powered_on=True
            ),
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE
            }
        )

        assert response.status_code == HTTPStatus.NOT_FOUND.value
        assert response.content_type == MIME_TYPE

    @with_app_context
    @mark.skip(reason='Standard-compliant implementation and test audit not complete.')
    def test_patch_request_with_no_data_is_bad_request(self, id: int=1):
        root_url = url_for(f'{BASE_URL}.update', id=id)
        response = self.client.patch(
            root_url,
            data=dict(),
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE
            }
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST.value
        assert response.content_type == MIME_TYPE


class TestLightDeleteAPI(object):
    '''Unit tests for the `DELETE` methods of the `LightAPI` class.'''

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
        client = app.test_client()
        setup_lights(app)

        self.app = app
        self.client = client
        self.api_ver = current_api.version

    def teardown_method(self, method: Callable):
        teardown_lights(self.app)
        del self.app
        del self.client

    @with_app_context
    def test_delete_collection_returns_no_content(self):
        root_url = url_for(f'{BASE_URL}.delete_all')
        response = self.client.delete(
            root_url,
            headers={'Accept': MIME_TYPE}
        )

        assert response.status_code == HTTPStatus.NO_CONTENT.value
        assert response.content_type == MIME_TYPE

    @with_app_context
    def test_delete_single_light_returns_no_content(self):
        root_url = url_for(f'{BASE_URL}.delete', id=1)
        response = self.client.delete(
            root_url,
            headers={'Accept': MIME_TYPE}
        )

        assert response.status_code == HTTPStatus.NO_CONTENT.value
        assert response.content_type == MIME_TYPE

    @with_app_context
    def test_delete_single_non_existent_light_is_not_found(self):
        root_url = url_for(f'{BASE_URL}.delete', id=10)
        response = self.client.delete(
            root_url,
            headers={'Accept': MIME_TYPE}
        )

        assert response.status_code == HTTPStatus.NOT_FOUND.value
        assert response.content_type == MIME_TYPE
