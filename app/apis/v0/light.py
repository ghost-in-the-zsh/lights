'''The REST API module for interacting with Lights.'''

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

from app.common.errors import (
    ObjectNotFoundError,
    DataIntegrityError,
    ValidationError
)
from app.services.light import (
    get_light_list,
    create_light,
    get_light,
    update_light,
    delete_light,
    delete_light_list
)
from ._schemas import LightSchema


class LightAPI(FlaskView):
    '''Class that maps API routes to endpoints.

    Class methods with the same name as the HTTP methods are matched
    automatically by Flask, but the `methods=[...]` list is given
    here for the sake of being explicit. Explicit is better than implicit.

    Class methods are grouped by HTTP method names and then by routes.
    '''
    @route('/', methods=['GET'], endpoint='api.v0.light.get_all')
    def index(self):
        '''Get all `Light` objects.'''
        lights = get_light_list()
        light_schema = LightSchema(many=True)
        serialized_lights = light_schema.dump(lights)
        response = jsonify({
            '_meta': {
                'stats': {
                    'total_count': len(lights),
                },
                'links': [{
                    'rel': 'self',
                    'href': url_for('api.v0.light.get_all', _external=True)
                }]
            },
            'lights': serialized_lights
        })
        return response, HTTPStatus.OK

    @route('/<int:id>', methods=['GET'], endpoint='api.v0.light.detail')
    def get(self, id: int):
        '''Get one `Light` object.'''
        try:
            light = get_light(id)
        except ObjectNotFoundError:
            abort(HTTPStatus.NOT_FOUND)

        light_schema = LightSchema()
        serialized_case = light_schema.dump(light)
        response = jsonify({'light': serialized_case})
        return response, HTTPStatus.OK

    @route('/', methods=['POST'], endpoint='api.v0.light.submit_new')
    def post(self):
        '''Create a new `Light` object.

        This response includes an extra HTTP `Location` header that lets
        the client know where the new resource can be found. This response
        includes the newly created object in the body.
        '''
        try:
            light = create_light(**request.json)
        except (DataIntegrityError, ValidationError) as e:
            abort(HTTPStatus.BAD_REQUEST, description=repr(e))
        except TypeError as e:
            abort(HTTPStatus.BAD_REQUEST, description=f'Data must be JSON-formatted.')

        light_url = url_for('api.v0.light.detail', id=light.id)
        light_schema = LightSchema(exclude=('_meta',))    # _meta.link goes in header
        light_json = light_schema.dump(light)
        response = jsonify({'light': light_json})

        # required in HTTP-201 responses
        response.headers['Location'] = light_url
        return response, HTTPStatus.CREATED

    @route('/<int:id>', methods=['PUT'], endpoint='api.v0.light.replace')
    def put(self, id: int):
        '''Replace a pre-existing `Light` object.

        This method is used to completely replace all the data of a given
        instance without creating a new one.

        This method will *not* create a new `Light` instance, even though it's
        an acceptable behavior[1].

        For partial updates, see `PATCH`.

        [1] https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PUT
        '''
        if not request.form:
            abort(HTTPStatus.BAD_REQUEST, description='No data provided')

        try:
            light = get_light(id)
            light.name = request.form.get('name')
            light.is_powered_on = request.form.get('is_powered_on')
            update_light(light)
            return {}, HTTPStatus.NO_CONTENT
        except ObjectNotFoundError as e:
            abort(HTTPStatus.NOT_FOUND)
        except (ValidationError, DataIntegrityError) as e:
            abort(HTTPStatus.BAD_REQUEST, description=repr(e))

    @route('/<int:id>', methods=['PATCH'], endpoint='api.v0.light.update')
    def patch(self, id: int):
        '''Partially update a pre-existing `Light` object.

        This method is meant to receive a set of operations[1] (i.e.
        delta/diff) to be applied to the resource identified by the URL
        as an atomic operation. A partially updated object must never
        be returned.

        For replacing full objects, see `PUT`.

        [1] https://williamdurand.fr/2014/02/14/please-do-not-patch-like-an-idiot/
        '''
        # FIXME: Previous implementation was not standard-compliant and has
        # been (temporarily?) removed.
        abort(HTTPStatus.NOT_IMPLEMENTED)

    @route('/', methods=['DELETE'], endpoint='api.v0.light.delete_all')
    def delete_all(self):
        '''Delete all the `Light`s.'''
        try:
            delete_light_list()
            return {}, HTTPStatus.NO_CONTENT
        except DataIntegrityError as e:
            abort(HTTPStatus.BAD_REQUEST, description=repr(e))


    @route('/<int:id>', methods=['DELETE'], endpoint='api.v0.light.delete')
    def delete(self, id: int):
        '''Delete the `Light` identified by the given ID, if it exists.

        You will find that some people say you should return `HTTP-200 OK`
        or `HTTP-204 No Content` when trying to delete non-existent rows.
        These arguments don't matter, though. What matters is the standard
        and it says that "this method is similar to the rm command in
        UNIX"[1].

        The `rm` command always throws an error when trying to delete a
        non-existent resource. For example:

            $ rm /path/to/nowhere
            rm: cannot remove '/path/to/nowhere': No such file or directory

        Therefore, we return `HTTP-404 Not Found` whenever the clients try
        to delete something that does not exist. Standards take precedence
        over personal opinions any day of the week.

        Also, note that idempotency does not include return codes[2].

        [1] https://tools.ietf.org/html/rfc7231#section-4.3.5
        [2] https://stackoverflow.com/a/24713946/4594973
        '''
        try:
            delete_light(id)
            return {}, HTTPStatus.NO_CONTENT
        except ObjectNotFoundError as e:
            abort(HTTPStatus.NOT_FOUND, description=repr(e))
        except DataIntegrityError as e:
            abort(HTTPStatus.BAD_REQUEST, description=repr(e))
