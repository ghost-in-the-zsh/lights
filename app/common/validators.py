'''Module for input validation classes.

Validators are used to check user inputs and make sure they follow some
basic rules before we accept their data and store it in the database.
'''

from abc import ABCMeta
from typing import Iterable, Any, Text, ClassVar
from inspect import isclass

from app.common.errors import ValidationError


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
            raise ValidationError(f'{self.error_message}: {value}')

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
            raise ValidationError(f'{self.error_message}: {value}')

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
            raise ValidationError(f'{self.error_message}: {type(value)}')

    def __repr__(self):
        return "<{}: class_type={} error_message='{}'>".format(
            self.__class__.__name__,
            self.class_type,
            self.error_message
        )
