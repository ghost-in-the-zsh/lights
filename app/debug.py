'''The debug extensions module.

This module contains any relevant extensions and/or utilities intended to
aid development and/or debugging. They MUST get automatically disabled
when running under a production environment.
'''

from flask_debugtoolbar import DebugToolbarExtension


# The toolbar extension internally relies on the app's DEBUG config; it
# gets auto-disabled in production without any changes.
toolbar = DebugToolbarExtension()
