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
from app.services.light import (
    get_light,
    get_light_list
)
from app.forms.light import LightForm


class LightView(FlaskView):
    '''Class that maps `Light`-related routes to endpoints.'''

    @route('/', methods=['GET'], endpoint='gui.light.get_all')
    def index(self):
        '''Get all `Light` objects.'''
        return render_template('lights/light_list.html', lights=get_light_list())

    @route('/<int:id>', methods=['GET'], endpoint='gui.light.detail')
    def get(self, id: int):
        '''Get one `Light` object.'''
        try:
            light = get_light(id)
            form = LightForm(obj=light)
            return render_template('lights/light_detail.html', form=form)
        except ObjectNotFoundError:
            abort(HTTPStatus.NOT_FOUND)

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
