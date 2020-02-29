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
        exclude = ('_is_powered_on', '_date_created')   # See below.

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
    # The model's private `_date_created` field must be treated as the
    # `_is_powered_on` field above for the same reasons.
    #
    # The `dump_only` option effectively marks this field as "read-only"
    # and cannot be set during de-serialization... because naming the
    # parameter `read_only` would've been too obvious.
    #
    # `DateTime` objects are stored in the database in naive form, i.e. they
    # are timezone-unaware without UTC offsets (i.e. `±HH:MM`). Because of
    # this, the `%z` part of the "%Y-%m-%dT%H:%M:%S%z" `format` is an empty
    # string, and gets serialized as such in its ISO-8601 format[1].
    #
    # This can cause problems for clients because `datetime` objects are
    # assumed to be in the *local* TZ unless otherwise specified. Since there's
    # no format string that will add the TZ info and we know they get stored in
    # UTC, we hard-code a `+HH:MM` offset of `+00:00` to add TZ information
    # until a better method is found. The serialized format is the same as that
    # from `.isoformat(timespec='seconds')`[1] and this is what clients should
    # use.
    #
    # [1] https://docs.python.org/3/library/datetime.html
    date_created = fields.DateTime(
        attribute='_date_created',
        format='%Y-%m-%dT%H:%M:%S+00:00',   # See above for hard-coded "+00:00" offset
        dump_only=True
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
