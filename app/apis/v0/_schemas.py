'''An internal/private module for model serialization schemas.

This package-private module prevents circular imports when sharing schemas
across API classes, especially for sub-resources.
'''

from flask_marshmallow.sqla import ModelSchema
from flask_marshmallow.fields import (
    URLFor,
    Hyperlinks
)

from app.models.light import Light


class LightSchema(ModelSchema):
    '''A schema to manage `Light` (de)serialization into/from JSON.'''

    class Meta:
        model = Light

    # allow programmatic API discovery and navigation
    _meta = Hyperlinks({
        'links': [
            {
                'rel': 'self',
                'href': URLFor('api.v0.light.detail', id='<id>', _external=True)
            }
        ]
    })
