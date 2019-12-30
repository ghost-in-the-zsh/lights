'''The error handlers module.'''

from flask import Response      # type annotation
from werkzeug.exceptions import HTTPException

from app.common.responses import error_response as api_error_response


def http_400_handler(error: HTTPException):
    '''Handler for `HTTP-400: Bad Request` error responses.'''
    return _handle_error(error)


def http_401_handler(error: HTTPException):
    '''Handler for `HTTP-401: Unauthorized` error responses.'''
    return _handle_error(error)


def http_403_handler(error: HTTPException):
    '''Handler for `HTTP-403: Forbidden` error responses.'''
    return _handle_error(error)


def http_404_handler(error: HTTPException):
    '''Handler for `HTTP-404: Not Found` error responses.'''
    return _handle_error(error)


def http_405_handler(error: HTTPException):
    '''Handler for `HTTP-405: Method Not Allowed` error responses.

    This response must include the HTTP `Allow` header.
    '''
    return _handle_error(error)


def http_406_handler(error: HTTPException):
    '''Handler for `HTTP-406: Not Acceptable` error responses.'''
    return _handle_error(error)


def http_500_handler(error: HTTPException):
    '''Handler for `HTTP-500: Internal Server Error` responses.

    Note that this handler will NOT get invoked automatically when
    the app is running under a `development` config/environment[1].
    Errors will be caught and a stack-trace will be displayed on the
    web-UI for debugging instead.

    To test this in a non-production environment, you can briefly edit a
    view to explicitly call `abort(HTTPStatus.INTERNAL_SERVER_ERROR)`.

    [1] https://stackoverflow.com/a/32040161/4594973
    '''
    return _handle_error(error)


def http_501_handler(error: HTTPException):
    '''Handler for `HTTP-501: Not Implemented` responses.'''
    return _handle_error(error)


def _handle_error(error: HTTPException) -> Response:
    '''Implementation function to actually handle the error.'''
    return api_error_response(error)
