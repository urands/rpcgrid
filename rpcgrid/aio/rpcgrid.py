from rpcgrid.aio.client import AsyncClient
from rpcgrid.aio.providers.local import LocalProvider
from rpcgrid.aio.server import AsyncServer, GlobalAsyncMethods
from rpcgrid.protocol.jsonrpc import JsonRPC


def register(func=None, name=None):
    if name is not None:
        GlobalAsyncMethods().add(name, func)
    else:
        GlobalAsyncMethods().add(func.__name__, func)


async def create(provider=None, protocol=None, loop=None):
    if protocol is None:
        protocol = JsonRPC()
    if provider is None:
        provider = LocalProvider(protocol)
    return await AsyncServer(provider, loop).create()


async def open(provider=None, protocol=None, loop=None):
    if protocol is None:
        protocol = JsonRPC()
    if provider is None:
        provider = LocalProvider(protocol)
    return await AsyncClient(provider, loop).open()
