from rpcgrid.client import Client
from rpcgrid.protocol.jsonrpc import JsonRPC
from rpcgrid.providers.local import LocalProvider
from rpcgrid.server import GlobalMethods, Server


def register(func=None, name=None):
    if name is not None:
        GlobalMethods().add(name, func)
    else:
        GlobalMethods().add(func.__name__, func)


def create(provider=None, protocol=None):
    if protocol is None:
        protocol = JsonRPC()
    if provider is None:
        provider = LocalProvider(protocol)
    return Server(provider)


def open(provider=None, protocol=None):
    if protocol is None:
        protocol = JsonRPC()
    if provider is None:
        provider = LocalProvider(protocol)
    return Client(provider)
