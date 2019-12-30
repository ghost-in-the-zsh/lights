import pytest

from app.common.errors import ValidationError
from app.common.validators import (
    MinLengthValidator,
    MaxLengthValidator
)


class TestMinLengthValidator(object):
    '''Unit tests for `MinLengthValidator` class.'''

    def test_zero_string_length_in_ctor_is_accepted(self):
        MinLengthValidator(min_length=0)

    def test_negative_string_length_in_ctor_raises_value_error(self):
        with pytest.raises(ValueError):
            MinLengthValidator(min_length=-1)

    def test_positive_string_length_in_ctor_is_accepted(self):
        MinLengthValidator(min_length=1)

    def test_non_integer_length_in_ctor_raises_type_error(self):
        with pytest.raises(TypeError):
            MinLengthValidator(min_length='hi there')

    def test_string_error_message_in_ctor_is_accepted(self):
        MinLengthValidator(min_length=0, error_message='error string')

    def test_non_string_error_message_in_ctor_raises_type_error(self):
        with pytest.raises(TypeError):
            MinLengthValidator(min_length=0, error_message=5)

    def test_minimum_length_string_is_valid(self):
        validator = MinLengthValidator(min_length=5)
        validator.validate('a' * 5)

    def test_minimum_length_iterable_is_valid(self):
        validator = MinLengthValidator(min_length=5)
        validator.validate(['a'] * 5)

    def test_below_minimum_length_string_raises_validation_error(self):
        validator = MinLengthValidator(min_length=5)
        with pytest.raises(ValidationError):
            validator.validate('a' * 4)

    def test_below_minimum_length_iterable_raises_validation_error(self):
        validator = MinLengthValidator(min_length=5)
        with pytest.raises(ValidationError):
            validator.validate(['a'] * 4)

    def test_non_iterable_validation_argument_raises_type_error(self):
        validator = MinLengthValidator(min_length=0)
        with pytest.raises(TypeError):
            validator.validate(2)

    def test_none_type_validation_argument_raises_validation_error(self):
        validator = MinLengthValidator(min_length=0)
        with pytest.raises(ValidationError):
            validator.validate(None)

    def test_repr_result_matches(self):
        validator = MinLengthValidator(min_length=2, error_message='bad bad')
        expected  = "<MinLengthValidator: min_length=2 error_message='bad bad'>"
        assert repr(validator) == expected


class TestMaxLengthValidator(object):
    '''Unit tests for `MaxLengthValidator` class.'''

    def test_zero_string_length_in_ctor_is_accepted(self):
        MaxLengthValidator(max_length=0)

    def test_negative_string_length_in_ctor_raises_value_error(self):
        with pytest.raises(ValueError):
            MaxLengthValidator(max_length=-1)

    def test_positive_string_length_in_ctor_is_accepted(self):
        MaxLengthValidator(max_length=1)

    def test_non_integer_length_in_ctor_raises_type_error(self):
        with pytest.raises(TypeError):
            MaxLengthValidator(max_length='hi there')

    def test_string_error_message_in_ctor_is_accepted(self):
        MaxLengthValidator(max_length=0, error_message='error string')

    def test_non_string_error_message_in_ctor_raises_type_error(self):
        with pytest.raises(TypeError):
            MaxLengthValidator(max_length=0, error_message=5)

    def test_maximum_length_string_is_valid(self):
        validator = MaxLengthValidator(max_length=5)
        validator.validate('a' * 5)

    def test_maximum_length_iterable_is_valid(self):
        validator = MaxLengthValidator(max_length=5)
        validator.validate(['a'] * 5)

    def test_beyond_maximum_length_string_raises_validation_error(self):
        validator = MaxLengthValidator(max_length=5)
        with pytest.raises(ValidationError):
            validator.validate('a' * 6)

    def test_beyond_maximum_length_iterable_raises_validation_error(self):
        validator = MaxLengthValidator(max_length=5)
        with pytest.raises(ValidationError):
            validator.validate(['a'] * 6)

    def test_non_iterable_validation_argument_raises_type_error(self):
        validator = MaxLengthValidator(max_length=0)
        with pytest.raises(TypeError):
            validator.validate(2)

    def test_none_type_validation_argument_raises_validation_error(self):
        validator = MaxLengthValidator(max_length=1)
        with pytest.raises(ValidationError):
            validator.validate(None)

    def test_repr_result_matches(self):
        validator = MaxLengthValidator(max_length=2, error_message='bad bad')
        expected  = "<MaxLengthValidator: max_length=2 error_message='bad bad'>"
        assert repr(validator) == expected
