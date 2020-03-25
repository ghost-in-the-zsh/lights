'''Module for input validation classes.

Validators are used to check user inputs and make sure they follow some
basic rules before we accept their data and store it in the database.
'''

import re
import hashlib
import logging
import requests

from abc import ABCMeta
from typing import Iterable, Any, Text, ClassVar
from inspect import isclass
from http import HTTPStatus
from http.client import responses
from requests.exceptions import RequestException

from app.common.errors import ModelValidationError


class _BaseValidator(metaclass=ABCMeta):
    '''The abstract base class for all validators.'''
    def validate(self, data: Any) -> None:
        raise NotImplementedError()


class MinLengthValidator(_BaseValidator):
    '''Validator to enforce a minimum length.

    Combine with `MaxLengthValidator` to enforce an expected length.
    '''
    def __init__(self, *, min_length: int, error_message: Text=None):
        if min_length < 0:
            raise ValueError('min_length < 0')
        if error_message is None or len(error_message) == 0:
            error_message = self.__class__.__name__ + f'(limit={min_length}) rejected data'

        self.min_length = min_length
        self.error_message = error_message

    def validate(self, value: Iterable):
        if not value or len(value) < self.min_length:
            raise ModelValidationError(f'{self.error_message}: {value}')

    def __repr__(self):
        return "<{}: min_length={} error_message='{}'>".format(
            self.__class__.__name__,
            self.min_length,
            self.error_message
        )


class MaxLengthValidator(_BaseValidator):
    '''Validator to enforce a maximum length.

    Combine with `MinLengthValidator` to enforce an expected length.
    '''
    def __init__(self, *, max_length: int, error_message: Text=None):
        if max_length < 0:
            raise ValueError('max_length < 0')
        if error_message is None or len(error_message) == 0:
            error_message = self.__class__.__name__ + f'(limit={max_length}) rejected data'

        self.max_length = max_length
        self.error_message = error_message

    def validate(self, value: Iterable):
        if not value or len(value) > self.max_length:
            raise ModelValidationError(f'{self.error_message}: {value}')

    def __repr__(self):
        return "<{}: max_length={} error_message='{}'>".format(
            self.__class__.__name__,
            self.max_length,
            self.error_message
        )


class ValueTypeValidator(_BaseValidator):
    '''Validator to verify a value is of type `bool`.'''
    def __init__(self, *, class_type: ClassVar, error_message: Text=None):
        if not isclass(class_type):
            raise TypeError('A class type is required.')

        if error_message is None or len(error_message) == 0:
            error_message = self.__class__.__name__ + f'(class_type={class_type}) rejected data'

        self.class_type = class_type
        self.error_message = error_message

    def validate(self, value: Any):
        if type(value) != self.class_type:
            raise ModelValidationError(f'{self.error_message}: {type(value)}')

    def __repr__(self):
        return "<{}: class_type={} error_message='{}'>".format(
            self.__class__.__name__,
            self.class_type,
            self.error_message
        )


class PasswordBreachValidator(_BaseValidator):
    '''Verifies whether a given password is known to have been exposed.

    The API at https://haveibeenpwned.com/API/v3 is used by this
    validator to verify whether a password is known to have been exposed
    in a known breach or not.

    This is done in a way that protects the password being verified from
    being exposed itself. The process works as follows:

        1. Generate a SHA-1 hash of the password;
        2. Send a 5-char prefix of the hash to the API over HTTPS (the
           full hash is *never* sent);
        3. Receive a list of 35-char hash suffixes from the API;
        4. Locally verify if the 35-char hash suffix of our local hash
           from (1) exists in the returned dataset on (3)

    This method prevents the remote service from identifying the hash
    of the password being checked as well as performing a reverse-lookup
    to figure out which password had originally been hashed. In fact, the
    remote service cannot even tell whether there was ever a matching hash
    suffix in the returned dataset or not, so the fact that they returned
    a dataset tells them nothing about our result.

    For more references, see:
        https://en.wikipedia.org/wiki/K-anonymity
        https://www.youtube.com/watch?v=hhUb5iknVJs
    '''
    def validate(self, password: Text) -> None:
        # There're some cases where we don't want to raise errors, but
        # don't want to fail silently either.
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.StreamHandler())  # defaults to `stderr`

        # hash the password and extract the hash prefix/suffix
        sha1hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        local_prefix = sha1hash[:5]
        local_suffix = sha1hash[5:].upper() # API replies in upper-case

        remote_host = 'https://api.pwnedpasswords.com'
        request_url = f'{remote_host}/range/{local_prefix}'
        try:
            response = requests.get(request_url)
        except RequestException:
            # XXX: I'd normally raise a `RuntimeError` here, but this
            # validator works on the basis of "best effort" and shouldn't
            # prevent a user from working with our system if the remote
            # system happens to be down, so we log and return instead.
            logger.warning(
                f'Failed to contact {remote_host}. The network connection '
                +'(or remote host) may be down or having other temporary '
                +'issues. Password verification SKIPPED!'
            )
            return

        if response.status_code != HTTPStatus.OK.value:
            # See previous notes.
            status = responses[response.status_code]
            logger.warning(
                f'Failed to fetch {request_url}: {status}. '
                +'Password verification SKIPPED!'
            )
            return

        # on average, we get 500 suffixes from the range API
        hashes = (line.split(':') for line in response.text.splitlines())
        matches = next((int(count) for suffix,count in hashes if local_suffix == suffix), 0)

        if matches > 0:
            hits = '{:,}'.format(matches)
            raise ModelValidationError(f'Unsafe password: Breached at least {hits} time(s)!')

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class TextPatternValidator(_BaseValidator):
    '''Validator to verify text patterns using regular expressions.'''

    LOWERCASE_ONLY = 'a-z'
    UPPERCASE_ONLY = 'A-Z'
    NUMBERS_ONLY = '0-9'
    LETTERS_ONLY = LOWERCASE_ONLY + UPPERCASE_ONLY
    ALPHA_CHARSET = LETTERS_ONLY + NUMBERS_ONLY
    DEFAULT_CHARSET = r'{charset}\.\-_'.format(charset=ALPHA_CHARSET)

    def __init__(self, *, pattern: Text, error_message: Text=None):
        if not isinstance(pattern, str):
            raise TypeError('pattern must be a string')

        if len(pattern) == 0:
            raise ValueError('pattern must not be empty')
        if error_message is None or len(error_message) == 0:
            error_message = self.__class__.__name__ + f'(pattern="{pattern}") rejected data'

        try:
            self._regexp = re.compile(pattern)
            self.error_message = error_message
        except re.error as e:
            raise ValueError(repr(e)) from e

    def validate(self, value: Any) -> None:
        try:
            if not self._regexp.match(value):
                raise ModelValidationError(self.error_message)
        except TypeError as e:
            raise ModelValidationError(self.error_message) from e

    def __repr__(self):
        return '<{}: pattern=\'{}\' error_message=\'{}\'>'.format(
            self.__class__.__name__,
            self._regexp.pattern,
            self.error_message
        )
