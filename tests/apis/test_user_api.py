'''The User API test module.

Note that the naming convention in this module (e.g. for classes,
module names, etc) is as it is so that `pytest` can find them via
introspection.
'''

# pylint: disable=no-member

import os
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
# from pytest import mark

from app import create_app
from app.settings import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH
)
from app.apis import current_api
from app.models import db
from app.models.user import User

from tests.utils import (
    setup_database,
    teardown_database,
    setup_users,
    teardown_users,
    with_app_context
)


BASE_URL = f'api.v{current_api.version}.user'
MIME_TYPE = 'application/json'


class TestUserAPI(object):
    '''Unit tests for the `UserAPI` class.'''

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
        setup_users(app)

        self.app = app
        self.client = client

    def teardown_method(self, method: Callable):
        teardown_users(self.app)
        del self.client
        del self.app

    @with_app_context
    def test_new_signup_is_created(self):
        url = url_for(f'{BASE_URL}.signup')
        data = dict(
            name='Khrono',
            email=f'{os.environ["USER"]}@localhost',
            password='Khrono-Lagarto-san',
            password2='Khrono-Lagarto-san',
        )
        response = self.client.post(
            url,
            data=json.dumps(data),
            headers={
                'Accept': MIME_TYPE,
                'Content-Type': MIME_TYPE,
            },
        )
        assert response.status_code == HTTPStatus.CREATED.value

        actual = response.json
        self_url = url_for(f'{BASE_URL}.detail', id=actual['user']['id'])
        expected = {
            'user': {
                'id': actual['user']['id'],
                'name': data['name'],
                'email': data['email'],
                'date_created': dt.now(tz.utc).isoformat(timespec='seconds')
            }
        }

        assert response.content_type == MIME_TYPE
        assert response.headers['Location'] == self_url
        assert expected == actual

    @with_app_context
    def test_signup_with_missing_data_is_bad_request(self):
        response = self.client.post(
            url_for(f'{BASE_URL}.signup'),
            headers={'Accept': MIME_TYPE},
            data={}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST.value

    @with_app_context
    def test_new_token_verification_is_ok(self):
        pass

    @with_app_context
    def test_used_token_verification_is_bad_request(self):
        pass

    @with_app_context
    def test_invalid_token_verification_is_bad_request(self):
        pass

    @with_app_context
    def test_see_myself_with_valid_token_is_ok(self):
        pass

    @with_app_context
    def test_see_myself_with_invalid_token_is_bad_request(self):
        pass

    @with_app_context
    def test_update_myself_with_valid_token_is_ok(self):
        pass

    @with_app_context
    def test_update_myself_with_invalid_token_is_bad_request(self):
        pass
