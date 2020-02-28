'''The errors module.

This module holds definitions for application-specific errors. Some of
the errors defined here may be intended to encapsulate other parts of the
system further (e.g. to decouple system layers from internal SQLAlchemy
exceptions).
'''


class ObjectNotFoundError(Exception):
    '''The object being searched for was not found.'''
    pass


class DataIntegrityError(Exception):
    '''The data being used causes integrity issues.

    This is generally expected to happen if attempts to add invalid
    data[1] to the database are made. There might be some cases where
    this error is more appropriate than a `ModelValidationError`.

    [1] Data is invalid when it violates database integrity constraints.
    '''
    pass

    '''
    pass


class ModelValidationError(Exception):
    '''The data being processed is rejected by the model as invalid.

    Normally, models process data on assignment. When a field receives an
    assignment, all available validators for it are run, when defined.
    These are expected to raise this error when their criteria is not met.
    '''
    pass


class InvalidPropertyError(Exception):
    '''The property being referenced does not match a field in the model.

    This is equivalent to a built-in `AttributeError`, but made into a
    separate exception to avoid confusion between internal errors and those
    intented for external clients.
    '''
    pass
