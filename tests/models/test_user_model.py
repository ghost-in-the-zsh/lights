# pylint: disable=no-member

import pytest

from typing import Callable, Dict, Text
from string import (
    ascii_letters,
    digits,
    punctuation
)
from time import time

from authlib.jose import jwt
from argon2 import PasswordHasher

from app import create_app
from app.settings import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_PASSWORD_HASH_LENGTH,
    AUTH_JWT_HEADER,
    AUTH_JWT_PAYLOAD_ISS,
    AUTH_JWT_PAYLOAD_EXP
)
from app.models.user import User
from app.common.validators import PasswordBreachValidator
from app.common.errors import (
    ModelValidationError,
    InvalidTokenError
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


class TestUserModelValidatorUnitTest(object):
    '''Unit tests for `models.user.User` class.'''

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
    def test_new_user_from_default_ctor_passes(self):
        # This test case is needed b/c the model has a custom `__init__`
        # method implementation, but we want to make sure it can still
        # be used just like any other model without one.
        user = User()

        assert user.id is None
        assert user.name is None
        # assert user.email is None
        assert user.password_hash is None

    @with_app_context
    def test_existing_user_values_match_expected(self):
        user = User.query.filter_by(id=1).one()
        assert user.name == 'User-1'
        assert user.password_hash is not None
        assert len(user.password_hash) == MAX_PASSWORD_HASH_LENGTH

    @with_app_context
    def test_valid_user_passes_validation_rules(self):
        user = User(**dict(
            name='example_name',
            password=DEFAULT_PASSWORD
        ))
        assert user.name == 'example_name'
        assert user.password_hash is not None

    def test_invalid_short_name_raises_validation_error(self):
        with pytest.raises(ModelValidationError):
            User(**dict(
                name='a'*(MIN_NAME_LENGTH-1),
                password=DEFAULT_PASSWORD
            ))

    def test_invalid_long_name_raises_validation_error(self):
        with pytest.raises(ModelValidationError):
            User(**dict(
                name='a'*(MAX_NAME_LENGTH+1),
                password=DEFAULT_PASSWORD
            ))

    @with_app_context
    def test_invalid_name_with_spaces_raises_validation_error(self):
        # This error should be raised by the `TextPatternValidator`
        with pytest.raises(ModelValidationError):
            User(**dict(
                name='Invalid Name with Spaces',
                password=DEFAULT_PASSWORD
            ))

    @with_app_context
    def test_readonly_password_hash_update_raises_attribute_error(self):
        user = User.query.filter_by(id=1).one()
        assert user.password_hash is not None

        # must be a read-only property
        with pytest.raises(AttributeError):
            user.password_hash = 'something'

    @with_app_context
    def test_setting_user_password_updates_password_hash(self):
        user = User.query.filter_by(id=1).one()
        assert user.password_hash is not None

        original = user.password_hash
        user.password = 'An Entirely Different Secret Here'
        updated = user.password_hash

        assert original != updated
        assert user.password_hash is not None

    @with_app_context
    def test_password_hashes_match(self, id=1):
        user = User.query.filter_by(id=id).one()

        hasher = PasswordHasher()
        assert hasher.verify(
            user.password_hash,
            f'User-App-Password-{id}'  # see `setup_users` function
        )

    @with_app_context
    def test_setting_breached_password_raises_validation_error(self, id=1):
        # This test case must be handled in a special way to prevent
        # *false positives*.
        #
        # To trigger the `PasswordBreachValidator`, we need a short crap
        # password that's *known* to have been compromised, but doing this
        # will cause the length validators first.
        #
        # Since this could lead to the *correct exception* being raised
        # for the *wrong reason* (and in this case it does, because we're
        # under the minimum length) we remove the password length
        # validators.
        #
        # Yes, this exceptional case requires some private member access, but
        # there's no other way to *100% guarantee* we're failing for the
        # correct reason.
        User._validators['_password_plaintext'] = [PasswordBreachValidator()]
        user = User.query.filter_by(id=id).one()
        with pytest.raises(ModelValidationError):
            user.password = '12345'

    @with_app_context
    def test_user_password_read_raises_attribute_error(self):
        user = User.query.filter_by(id=1).one()

        # `user.password` is a write-only property and
        # reads must not be allowed
        with pytest.raises(AttributeError):
            assert user.password is not None

    @with_app_context
    def test_invalid_short_name_raises_model_validation_error_on_assignment(self):
        user = User.query.filter_by(id=1).one()
        with pytest.raises(ModelValidationError):
            user.name = 'a' * (MIN_NAME_LENGTH-1)

    @with_app_context
    def test_invalid_long_name_raises_model_validation_error_on_assignment(self):
        user = User.query.filter_by(id=1).one()
        with pytest.raises(ModelValidationError):
            user.name = 'a' * (MAX_NAME_LENGTH+1)

    @with_app_context
    def test_valid_token_generation_passes(self):
        user = User.query.filter_by(id=1).one()
        timestamp = int(time())
        payload = {
            'iss': AUTH_JWT_PAYLOAD_ISS,
            'sub': user.id,
            'iat': timestamp,
            'nbf': timestamp,
            'exp': timestamp + AUTH_JWT_PAYLOAD_EXP
        }
        private_key = self.app.config['SECRET_KEY']

        # create a token independent from the User model's logic
        # to compare against; after ensuring a match between our token
        # and the `User` model's token, verify the claims made by the
        # `User` are valid.
        expected_token = jwt.encode(AUTH_JWT_HEADER, payload, private_key).decode('utf-8')
        actual_token = user.generate_token()
        actual_claims = jwt.decode(actual_token, private_key)

        assert expected_token == actual_token
        assert actual_claims.header == AUTH_JWT_HEADER
        assert actual_claims == payload

        # raises exception on failure
        actual_claims.validate()

    @with_app_context
    def test_valid_token_generation_with_custom_ttl_passes(self, token_ttl: int=10):
        user = User.query.filter_by(id=1).one()
        timestamp = int(time())
        payload = {
            'iss': AUTH_JWT_PAYLOAD_ISS,
            'sub': user.id,
            'iat': timestamp,
            'nbf': timestamp,
            'exp': timestamp + token_ttl
        }
        private_key = self.app.config['SECRET_KEY']

        expected_token = jwt.encode(AUTH_JWT_HEADER, payload, private_key).decode('utf-8')
        actual_token = user.generate_token(token_ttl=token_ttl)
        actual_claims = jwt.decode(actual_token, private_key)

        assert expected_token == actual_token
        assert actual_claims.header == AUTH_JWT_HEADER
        assert actual_claims == payload

        # raises exception on failure
        actual_claims.validate()

    @with_app_context
    def test_loading_user_from_valid_token_passes(self, uid=1):
        timestamp = int(time())
        payload = {
            'iss': AUTH_JWT_PAYLOAD_ISS,
            'sub': uid,
            'iat': timestamp,
            'nbf': timestamp,
            'exp': timestamp + AUTH_JWT_PAYLOAD_EXP
        }
        private_key = self.app.config['SECRET_KEY']

        auth_token = jwt.encode(AUTH_JWT_HEADER, payload, private_key).decode('utf-8')
        user = User.from_token(auth_token)

        assert user.id == uid

    @with_app_context
    def test_loading_user_from_invalid_token_raises_invalid_token_error(self, uid=1):
        timestamp = int(time())
        payload = {
            'iss': AUTH_JWT_PAYLOAD_ISS,
            'sub': uid,
            'iat': timestamp,
            'nbf': timestamp,
            'exp': timestamp + AUTH_JWT_PAYLOAD_EXP
        }
        private_key = b'not your app server key'
        auth_token = jwt.encode(AUTH_JWT_HEADER, payload, private_key).decode('utf-8')

        with pytest.raises(InvalidTokenError):
            User.from_token(auth_token)
