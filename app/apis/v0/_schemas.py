'''An internal/private module for model serialization schemas.

This package-private module prevents circular imports when sharing schemas
across API classes, especially for sub-resources.
'''

from flask_marshmallow.sqla import ModelSchema
from flask_marshmallow.fields import (
    URLFor,
    Hyperlinks
)
from marshmallow import (
    fields,
    validate
)

from app.settings import (
    TRUTHY,
    FALSEY,
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH
)
from app.models.light import Light


class LightSchema(ModelSchema):
    '''A schema to manage `Light` (de)serialization into/from JSON.'''

    class Meta:
        model = Light
        exclude = ('_is_powered_on',)   # See above.

    name = fields.String(
        validate=[
            validate.Length(min=MIN_NAME_LENGTH, max=MAX_NAME_LENGTH)
        ]
    )
    # The model's private `_is_powered_on` field needs to be overriden so
    # that it can be presented by its property name, `is_powered_on`, to
    # clients. The private field also needs to be excluded to prevent name
    # clashes between fields that are manually defined and those that are
    # inferred[1].
    #
    # [1] https://stackoverflow.com/a/55892116/4594973
    is_powered_on = fields.Boolean(
        truthy=TRUTHY,
        falsey=FALSEY
    )

    # allow programmatic API discovery and navigation
    _meta = Hyperlinks({
        'links': [
            {
                'rel': 'self',
                'href': URLFor('api.v0.light.detail', id='<id>', _external=True)
            }
        ]
    })
