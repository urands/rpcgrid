from typing import Any, Callable, Type

from rpcgrid.client import AsyncClient
from rpcgrid.protocol.base import BaseProtocol
from rpcgrid.protocol.jsonrpc import JsonRPC
from rpcgrid.providers.base import BaseProvider
from rpcgrid.providers.local import LocalProvider
from rpcgrid.server import AsyncServer, GlobalAsyncMethods


def register(func: Callable = None, name: str = None) -> None:
    if name is not None:
        GlobalAsyncMethods().add(name, func)
    else:
        GlobalAsyncMethods().add(func.__name__, func)


def server(
    provider: Type[BaseProvider] = None,
    protocol: Type[BaseProtocol] = None,
    loop: Any = None,
) -> AsyncServer:
    if protocol is None:
        protocol = JsonRPC()
    if provider is None:
        provider = LocalProvider(protocol=protocol, loop=loop)
    return AsyncServer(provider, loop=loop).create()


def client(
    provider: Type[BaseProvider] = None,
    protocol: Type[BaseProtocol] = None,
    loop: Any = None,
) -> AsyncClient:
    if protocol is None:
        protocol = JsonRPC()
    if provider is None:
        provider = LocalProvider(protocol=protocol, loop=loop)
    return AsyncClient(provider, loop=loop).open()
