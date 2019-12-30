'''Top-level package for REST-based API services.

This is a versioned API and uses semantic versioning[1] for naming. Only
the major version is included in the URLs and changes may be made for
minor/patch versions without altering them.

This module imports nested API package modules into its scope in order
to make it easier for other parts of the system to use without propagating
version-specific information around.

In principle, this should allow updating API versions without also having
to update imports in other parts of the system.

[1] https://semver.org
'''

from . import v0 as current_api
