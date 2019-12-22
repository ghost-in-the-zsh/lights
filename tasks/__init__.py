'''The tasks package for Python invoke commands.

The commands are namespaced on a per-module basis to keep things
organized and tidy.

Note: Parameter type annotations cause the `invoke` command to complain
and fail with errors.
'''

from invoke import Collection

from . import (
    test,
    report
)

ns = Collection()
ns.add_collection(test)
ns.add_collection(report)
