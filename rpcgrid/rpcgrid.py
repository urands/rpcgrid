from rpcgrid.client import AsyncClient
from rpcgrid.protocol.jsonrpc import JsonRPC
from rpcgrid.providers.local import LocalProvider
from rpcgrid.server import AsyncServer, GlobalAsyncMethods


def register(func=None, name=None):
    if name is not None:
        GlobalAsyncMethods().add(name, func)
    else:
        GlobalAsyncMethods().add(func.__name__, func)


def create(provider=None, protocol=None, loop=None):
    if protocol is None:
        protocol = JsonRPC()
    if provider is None:
        provider = LocalProvider(protocol=protocol, loop=loop)
    return AsyncServer(provider, loop=loop).create()


def open(provider=None, protocol=None, loop=None):
    if protocol is None:
        protocol = JsonRPC()
    if provider is None:
        provider = LocalProvider(protocol=protocol, loop=loop)
    return AsyncClient(provider, loop=loop).open()
