from types import FunctionType
from typing import AnyStr, Callable, Coroutine, Optional

from rpcgrid.client import AsyncClient
from rpcgrid.protocol.base import BaseProtocol
from rpcgrid.protocol.jsonrpc import JsonRPC
from rpcgrid.providers.base import BaseProvider
from rpcgrid.providers.local import LocalProvider
from rpcgrid.server import (
    AsyncServer,
    ExecuterServerProvider,
    GlobalAsyncMethods,
)


def register(*args, **kwargs):
    def register_subdecorator(func: Callable, name: AnyStr = None):
        if name is not None:
            GlobalAsyncMethods().add(name, func)
        else:
            GlobalAsyncMethods().add(func.__name__, func)

    if len(args) == 1 and isinstance(args[0], FunctionType):
        return register_subdecorator(args[0])
    return register_subdecorator


def server(
        provider: Optional[BaseProvider] = None,
        protocol: Optional[BaseProtocol] = None,
        loop=None,
        executor: str = None,
) -> Coroutine:
    if protocol is None:
        protocol = JsonRPC()
    if provider is None:
        provider = LocalProvider(protocol=protocol, loop=loop)
    if executor is None:
        return AsyncServer(provider, loop=loop).create()
    else:
        return ExecuterServerProvider(provider, loop=loop).create(executor)


def client(
        provider: Optional[BaseProvider] = None,
        protocol: Optional[BaseProtocol] = None,
        loop=None,
) -> Coroutine:
    if protocol is None:
        protocol = JsonRPC()
    if provider is None:
        provider = LocalProvider(protocol=protocol, loop=loop)
    return AsyncClient(provider, loop=loop).open()
