import sys

# import warnings
# import pkg_resources # noqa: F401
from rpcgrid.rpcgrid import create, open, register  # noqa: F401

if sys.version_info < (3, 5):
    raise EnvironmentError(
        "Python 3.5 or above is required. "
        "Note that support for Python 3.5 will be removed in web3.py v5"
    )


# __version__ = pkg_resources.get_distribution("rpcgrid").version

__version__ = "0.0.1"
