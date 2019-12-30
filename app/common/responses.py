'''The responses module.

Custom HTTP Responses that the application needs to use in some cases are
defined here.
'''

from http import HTTPStatus

from flask import (
    current_app,
    jsonify,
    request,
    make_response,
    Response        # type annotation
)
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import (
    HTTPException,  # type annotation
    NotFound
)


def error_response(error: HTTPException) -> Response:
    '''Returns an HTTP Response with a JSON payload.

    This is mainly intended for REST API consumption based on client
    requests by means of the HTTP `Accept: <mime-type>` header (i.e. when
    they request content in `application/json` format).
    '''
    response_headers = dict()
    response_data = {
        'error_text': HTTP_STATUS_CODES.get(error.code, 'Unknown Error'),
        'description': error.description,
        'url': request.url
    }
    if error.code == HTTPStatus.METHOD_NOT_ALLOWED.value:
        # We're returning an HTTP-405 Method Not Allowed, which "MUST
        # include an Allow header containing a list of valid methods for
        # the requested resource"[1]. We also let the client know which
        # method they erroneously used in the original request, because
        # we're nice.
        #
        # Normally, the `request.url_rule.methods` would be the place to
        # find the valid methods for the requested endpoint, but in this
        # case, we're handling an invalid method that raised a
        # `werkzeug.routing.MethodNotAllowed` error, so we must get the
        # methods from `request.routing_exception.valid_methods` instead.
        #
        # [1] https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
        #
        response_headers['Allow'] = ', '.join(request.routing_exception.valid_methods)
        response_data['request_method'] = request.method

    response = make_response(jsonify(**response_data))
    response.status_code = error.code
    for header,value in response_headers.items():
        response.headers[header] = value

    return response
