'''The errors module.

This module holds definitions for application-specific errors. Some of
the errors defined here may be intended to encapsulate other parts of the
system further (e.g. to decouple system layers from internal SQLAlchemy
exceptions).
'''


class BaseError(Exception):
    '''The base error class for application-specific errors.

    This error is not meant to be raised directly. Rather, it's meant to
    be the foundation of the error class hierarchy in this system.

    Catching this error is directly discouraged in most cases. It's
    generally recommended that you catch the more specific errors defined
    below.
    '''
    pass


class ObjectNotFoundError(BaseError):
    '''The object being searched for was not found.'''
    pass


class DataIntegrityError(BaseError):
    '''The data being used causes integrity issues.

    This is generally expected to happen if attempts to add invalid
    data[1] to the database are made. There might be some cases where
    this error is more appropriate than a `ModelValidationError`.

    [1] Data is invalid when it violates database integrity constraints.
    '''
    pass


class UniqueObjectExpectedError(BaseError):
    '''A single unique object was expected, but ended up with several.

    This can happen when the search criteria for finding a single object
    is too lax, vague, and/or ambiguous, causing the system to return
    several results in a single query.

    In such a case, the client should either narrow down the search
    criteria or use a call that explicitly returns a list of objects.
    '''
    pass


class ModelValidationError(BaseError):
    '''The data being processed is rejected by the model as invalid.

    Normally, models process data on assignment. When a field receives an
    assignment, all available validators for it are run, when defined.
    These are expected to raise this error when their criteria is not met.
    '''
    pass


class InvalidPropertyError(BaseError):
    '''The property being referenced does not match a field in the model.

    This is equivalent to a built-in `AttributeError`, but made into a
    separate exception to avoid confusion between internal errors and those
    intented for external clients.
    '''
    pass
