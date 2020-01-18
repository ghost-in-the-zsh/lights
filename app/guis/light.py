'''The Lights GUI views module.

This module defines the views and associated routes. It relies on
a separate module with specific "business-logic" to access and/or
modify the data as needed.
'''

from http import HTTPStatus

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    abort
)
from flask_classful import (
    FlaskView,
    route
)

from app.common.errors import (
    ObjectNotFoundError,
    DataIntegrityError
)
from app.models.light import Light


class LightView(FlaskView):
    '''Class that maps `Light`-related routes to endpoints.'''

    @route('/', methods=['GET'], endpoint='gui.light.get_all')
    def index(self):
        '''Get all `Light` objects.'''
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/<int:id>', methods=['GET'], endpoint='gui.light.detail')
    def get(self, id: int):
        '''Get one `Light` object.'''
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/create', methods=['GET'], endpoint='gui.light.request_new')
    def create_requested(self):
        '''Gets the new `Light` form.'''
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/create', methods=['POST'], endpoint='gui.light.submit_new')
    def create_submitted(self):
        '''Process the submitted form for a new `Light`.'''
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/<int:id>', methods=['POST'], endpoint='gui.light.update')
    def update(self, id: int):
        '''Update an existing `Light`.'''
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/<int:id>/delete', methods=['POST'], endpoint='gui.light.delete')
    def delete(self, id: int):
        '''Deletes a `Light` from the system.'''
        abort(HTTPStatus.NOT_IMPLEMENTED)
