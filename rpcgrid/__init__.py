import sys

# import warnings
# import pkg_resources # noqa: F401
from rpcgrid.rpcgrid import server, client, register  # noqa: F401

if sys.version_info < (3, 6):
    raise EnvironmentError(
        "Python 3.6 or above is required. "
        "Note that support for Python 3.6 will be test on actions"
    )


# __version__ = pkg_resources.get_distribution("rpcgrid").version

__version__ = "1.0.1"
