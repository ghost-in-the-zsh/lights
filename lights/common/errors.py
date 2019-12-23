'''The errors module.

This module holds definitions for application-specific errors. Some of
the errors defined here may be intended to encapsulate other parts of the
system further (e.g. to decouple system layers from internal SQLAlchemy
exceptions).
'''


class ValidationError(Exception):
    '''The data being processed is rejected as invalid.

    This error is generally raised by model field validators.
    '''
    pass
