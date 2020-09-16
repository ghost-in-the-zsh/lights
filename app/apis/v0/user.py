'''The user management API module.

This API allows users to authenticate with the system and perform other
user-centric tasks. What follows is a basic "feature design document"
with an overview of the features/functionality this is meant to enable.


## User Account Registration

A user may sign up for a new app account by using an email and a
password/phrase.


## User Account Verification

When a new account has been registered, an email with a confirmation token
is sent to the user's email address. The user must click this link in order
to confirm activation of this account.


## User Account Sign In

A user can sign into the system by using their credentials. On successful,
sign in, app returns a JWT that the user must include in subsequent
requests that require authentication.


## User Account Sign Out

A user can sign out of the system, which in turn, will cause app to
revoke the user token granted at sign in.
'''

from typing import Text
from http import HTTPStatus

from flask import (
    jsonify,
    url_for,
    abort,
    request
)
from flask_classful import (
    FlaskView,
    route
)

from app.models.user import User
from app.common.errors import (
    ObjectNotFoundError,
    DataIntegrityError,
    ModelValidationError,
    InvalidTokenError
)
from app.services.user import (
    get_user_list,
    create_user,
    get_user,
    update_user,
    delete_user,
    delete_user_list,
)
from ._schemas import UserSchema


class UserAPI(FlaskView):
    '''Class that maps API routes to endpoints.

    Class methods with the same name as the HTTP methods are matched
    automatically by Flask, but the `methods=[...]` list is given
    here for the sake of being explicit. Explicit is better than implicit.

    Class methods are grouped by HTTP method names and then by routes.
    '''
    @route('/', methods=['GET'], endpoint='api.v0.user.get_all')
    def index(self):
        '''Get all `User` objects, if you have an admin token.'''
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/<int:id>', methods=['GET'], endpoint='api.v0.user.detail')
    def get(self, id: int):
        '''Get one `User` object, if you have an admin token.'''
        abort(HTTPStatus.NOT_IMPLEMENTED)

    # XXX: Avoid `register` as method name; it collides with
    #      `FlaskView.register`.
    @route('/signup', methods=['POST'], endpoint='api.v0.user.signup')
    def signup(self):
        '''Create a new `User` object for a new account.'''
        try:
            user = create_user(**request.json)
        except (DataIntegrityError, ModelValidationError) as e:
            abort(HTTPStatus.BAD_REQUEST, description=repr(e))
        except TypeError as e:
            abort(HTTPStatus.BAD_REQUEST, description='Data must be JSON-formatted.')

        user_url = url_for('api.v0.user.detail', id=user.id)
        user_schema = UserSchema(exclude=('_meta', 'is_admin', 'is_verified'))
        user_json = user_schema.dump(user)
        response = jsonify({'user': user_json})

        # required in HTTP-201 responses
        response.headers['Location'] = user_url
        return response, HTTPStatus.CREATED

    @route('/verify', methods=['POST'], endpoint='api.v0.user.verify')
    def verify(self, token: Text):
        '''Verify a new account with a verification token.'''
        try:
            User.verify_token(token)
        except (DataIntegrityError, InvalidTokenError) as e:
            abort(HTTPStatus.BAD_REQUEST, repr(e))

    @route('/myself', methods=['GET'], endpoint='api.v0.user.see_myself')
    def see_myself(self, token: Text):
        '''Get your `User` object, if you have a token.'''
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/myself', methods=['PUT'], endpoint='api.v0.user.update_myself')
    def update_myself(self, token: Text):
        '''Update your `User` object, if you have a token.'''
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/<int:id>', methods=['DELETE'], endpoint='api.v0.user.delete')
    def delete(self, id: int):
        '''Delete the `User` identified by the given ID, if it exists and
        you're an admin.

        You will find that some people say you should return `HTTP-200 OK`
        or `HTTP-204 No Content` when trying to delete non-existent rows.
        These arguments don't matter, though. What matters is the standard
        and it says that "this method is similar to the rm command in
        UNIX"[1].

        The `rm` command always throws an error when trying to delete a
        non-existent resource. For example:

        ```
        $ rm /path/to/nowhere
        rm: cannot remove '/path/to/nowhere': No such file or directory
        ```

        Therefore, we return `HTTP-404 Not Found` whenever the clients try
        to delete something that does not exist. Standards take precedence
        over personal opinions any day of the week.

        Also, note that idempotency does not include return codes[2].

        [1] https://tools.ietf.org/html/rfc7231#section-4.3.5
        [2] https://stackoverflow.com/a/24713946/4594973
        '''
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/', methods=['DELETE'], endpoint='api.v0.user.delete_all')
    def delete_all(self):
        '''Delete all the `User`s, except yourself, if you have an admin
        token.
        '''
        abort(HTTPStatus.NOT_IMPLEMENTED)
