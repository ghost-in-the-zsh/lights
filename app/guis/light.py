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
        # Could've sorted at the DB level with:
        #   `db.session.query(Light).order_by(Light.name).all()`
        # but chose to preserve the abstraction given by the services
        # layer.
        return render_template(
            'lights/light_list.html',
            lights=sorted(
                get_light_list(),
                key=lambda light: light.name
            )
        )

    @route('/<int:id>', methods=['GET'], endpoint='gui.light.detail')
    def get(self, id: int):
        '''Get one `Light` object.'''
        try:
            light = get_light(id=id)
            form = LightForm(obj=light)
            return render_template('lights/light_detail.html', form=form)
        except ObjectNotFoundError:
            abort(HTTPStatus.NOT_FOUND)

    @route('/create', methods=['GET'], endpoint='gui.light.request_new')
    def create_requested(self):
        '''Gets the new `Light` form.'''
        form = LightForm()
        return render_template('lights/light_create.html', form=form)

    @route('/create', methods=['POST'], endpoint='gui.light.submit_new')
    def create_submitted(self):
        '''Process the submitted form for a new `Light`.'''
        # This method would need an implementation if the current
        # AJAX-based implementation is replaced by an HTML <form>
        # that actually targets this endpoint.
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/<int:id>', methods=['POST'], endpoint='gui.light.update')
    def update(self, id: int):
        '''Update an existing `Light`.'''
        # Updates are currently handled via the API endpoint, not the GUI.
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/<int:id>/delete', methods=['POST'], endpoint='gui.light.delete')
    def delete(self, id: int):
        '''Deletes a `Light` from the system.'''
        # Deletes are currently handled via the API endpoint, not the GUI.
        abort(HTTPStatus.NOT_IMPLEMENTED)
