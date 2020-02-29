'''The data filters module.

Filters may exclude, format, or transform data in some way. These are
primarily for use in Jinja2 templates, though they can be used elsewhere.
'''

from typing import Text
from datetime import datetime

from babel import dates


def datetime_delta_filter(dtv: datetime, precision: Text='second', threshold: float=0.75) -> Text:
    '''Formatting filter for `datetime` objects.

    :param dtv: The `datetime` object to be formatted.

    :param precision: The smallest unit of measure to display. Options
    are: 'year', 'month', 'week', 'day', 'hour', 'minute', or 'second'.

    :param threshold: A real value that determines when to "round up" to
    a higher unit. By default, we round up when we're 75% of the way there
    or closer.
    '''
    if not isinstance(dtv, datetime):
        return None

    # pos/neg result allows `add_direction` option to work
    # correctly, showing the times as being in the future
    # or in the past respectively
    dtv = dtv.replace(tzinfo=None) - datetime.utcnow()
    return dates.format_timedelta(
        dtv,
        granularity=precision,
        threshold=threshold,
        add_direction=True
    )
