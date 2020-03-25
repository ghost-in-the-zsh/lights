'''The User database model.'''

# pylint: disable=no-member

from typing import Text, Any, Dict
from time import time

from flask import current_app as app

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    CheckConstraint,
    ForeignKey
)
from sqlalchemy.orm import validates
from sqlalchemy.exc import IntegrityError

# https://docs.authlib.org/en/latest/specs/rfc7519.html
# https://en.wikipedia.org/wiki/JSON_Web_Token
from authlib.jose import jwt
from authlib.jose.errors import (
    JoseError,
    BadSignatureError
)

from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHash
)

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
from app.common.errors import (
    DataIntegrityError,
    InvalidTokenError,
    InvalidCredentialsError
)
from app.common.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    PasswordBreachValidator,
    TextPatternValidator
)
from app.models import db


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'public'}

    _validators = {
        'name': [
            MinLengthValidator(min_length=MIN_NAME_LENGTH),
            MaxLengthValidator(max_length=MAX_NAME_LENGTH),
            # The regexp does not need to include length requirements
            # because the other validators already account for those.
            TextPatternValidator(pattern=r'^[{charset}]+$'.format(
                charset=TextPatternValidator.DEFAULT_CHARSET
            ))
        ],
        '_password_plaintext': [
            # Validation of plaintexts prior to hashing is done to
            # let users know that their crappy passwords are crappy ^-^
            MinLengthValidator(min_length=MIN_PASSWORD_LENGTH),
            MaxLengthValidator(max_length=MAX_PASSWORD_LENGTH),
            PasswordBreachValidator()
        ],
        '_password_hash': [
            # Properly hashed passwords are expected to be exactly
            # `MAX_PASSWORD_HASH_LENGTH` chars long. Failing validation
            # is most likely indicative of a bug in code where passwords
            # are not being hashed correctly.
            MinLengthValidator(min_length=MAX_PASSWORD_HASH_LENGTH),
            MaxLengthValidator(max_length=MAX_PASSWORD_HASH_LENGTH)
        ]
    }

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(MAX_NAME_LENGTH),
        CheckConstraint(f'length(name) >= {MIN_NAME_LENGTH} and length(name) <= {MAX_NAME_LENGTH}'),
        index=True,
        unique=True,
        nullable=False
    )
    _password_hash = db.Column(
        'password_hash',
        db.String(MAX_PASSWORD_HASH_LENGTH),
        CheckConstraint(f'length(password_hash) = {MAX_PASSWORD_HASH_LENGTH}'),
        nullable=False
    )

    def __init__(self, **kwargs: Dict):
        '''Initialize the `User` instance.

        The following are the *required* entries for the `kwargs` dictionary:

        :param name: User's name.
        :param password: User's plaintext password. This is hashed before storing.

        Most of the time, implementing this method is unnecessary because
        the fields can be auto-assigned when their names match those of the
        fields they are for. What makes it necessary in this case is that
        we must hash the user's password before storing it in the database
        backend, which makes use of fields that are either not publicly
        writable by clients or don't directly exist in the database table.
        '''
        super().__init__(**kwargs)

        def _set_field(field: Text, value: Any) -> None:
            if value:
                setattr(self, field, value)

        _set_field('name', kwargs.get('name', None))
        _set_field('password', kwargs.get('password', None))

    @property
    def password(self) -> Text:
        '''A workaround property to enable the `@password.setter`.

        Access to this property is denied for security reasons and always
        raises an error. The error raised may change without prior notice
        or guarantees. DO NOT READ THIS FIELD. If you do, you're doing it
        wrong.
        '''
        raise AttributeError('This is a write-only property. It cannot be read.')

    @password.setter
    def password(self, plaintext: Text) -> None:
        '''A method for securely (re)setting the `User`'s password.

        :param plaintext: The password for this user, prior to hashing.

        This method's implementation runs the validators against the
        plaintext and then hashes it for storage. The plaintext password
        is *never* retained or stored.

        This method exists because it enables the very natural use-case
        of updating a `User`'s password as follows:
        ```
        user.password = ...
        ```
        This is especially useful because the `password_hash` field is
        read-only[1] and the only other way to set a password is to
        create a new `User` instance. This implementation addresses this
        use-case by exposing this write-only property for this purpose.

        [1] This is done to prevent external sources from trying to
        invent with their own hashing approaches and/or clobbering it in
        some way, which would prevent valid user authentication attempts
        later on.
        '''
        # we must run the validators explicitly b/c there's no table column
        # named `_password_plaintext` or a field that can be set for the
        # validators to auto-fire/run
        self._validate('_password_plaintext', plaintext)

        hasher = PasswordHasher()
        self._password_hash = hasher.hash(plaintext)

    @property
    def password_hash(self) -> Text:
        return self._password_hash

    def verify_password(self, plaintext: Text) -> None:
        hasher = PasswordHasher()
        try:
            hasher.verify(self._password_hash, plaintext)
        except(VerifyMismatchError, VerificationError, InvalidHash) as e:
            raise InvalidCredentialsError('Incorrect credentials provided') from e

        # Whenever Argon2 or `argon2-cffi` default hashing parameters
        # change, passwords must be rehashed ASAP. We do that automati-
        # cally, if needed, on successful user authentication.
        #
        # XXX: Hashing changes *may* require column length updates.
        #      See `app.settings`.
        if hasher.check_needs_rehash(self._password_hash):
            self._password_hash = hasher.hash(plaintext)

    def generate_token(self, *, token_ttl: int=AUTH_JWT_PAYLOAD_EXP) -> Text:
        '''Generate a token for this user.

        :param token_ttl: Time before the token expires, in seconds.

        This token can be used to identify and authorize a given user to
        perform certain tasks/operations in the system.
        '''
        # only interested in seconds; truncate fractional part
        timestamp = int(time())
        payload = {
            'iss': AUTH_JWT_PAYLOAD_ISS,
            'sub': self.id,
            'iat': timestamp,
            'nbf': timestamp,
            'exp': timestamp + int(token_ttl)   # `int()` forces error in some cases
        }
        return jwt.encode(
            AUTH_JWT_HEADER,
            payload,
            app.config['SECRET_KEY']
        ).decode('utf-8')

    @staticmethod
    def from_token(token: Text):    # type: User
        '''Load a `User` from the given JWT.

        :param token: A JWT for authentication purposes.
        :raises InvalidTokenError: The token received failed validation (e.g. expired).
        '''
        try:
            claims = jwt.decode(token, app.config['SECRET_KEY'])
            claims.validate()

            # Since we know the claims are valid, we know the token must've
            # been generated by an existing User, so we should always be
            # able to find the given subject ID
            return User.query.get(claims['sub'])
        except BadSignatureError as e:
            # The `BadSignatureError` has an empty string as `description`,
            # which is not useful, so we set it here.
            raise InvalidTokenError('Token was rejected. Reason: Bad signature') from e
        except JoseError as e:
            # `authlib.jose.errors.JoseError` is the base class for all
            # errors including `BadSignatureError`, `ExpiredTokenError`,
            # and others; in our case, they all mean the token is invalid
            # and this is what the client needs to know (but simplified)
            raise InvalidTokenError(e.description) from e

    @validates('name')
    def _validate_name(self, attribute_name: Text, name: Text) -> Text:
        return self._validate(attribute_name, name)

    @validates('_password_hash')
    def _validate_password_hash(self, attribute_name: Text, password_hash: Text) -> Text:
        return self._validate(attribute_name, password_hash)

    def _validate(self, attribute_name: Text, attribute_value: Text) -> Text:
        for validator in User._validators[attribute_name]:
            validator.validate(attribute_value)
        return attribute_value

    def __repr__(self):
        return "<{}: id={} name='{}'>".format(
            self.__class__.__name__,
            self.id,
            self.name
        )
