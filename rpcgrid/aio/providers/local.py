import asyncio

from rpcgrid.aio.providers.base import AsyncBaseProvider


class LocalProvider(AsyncBaseProvider):
    _protocol = None
    _queue = None
    _remote_queue = None
    _timeout = None

    def __init__(self, protocol):
        self._protocol = protocol
        self._queue = asyncio.Queue()

    def is_connected(self):
        return True

    def set_remote_provider(self, remote):
        self._remote_queue = remote.provider._queue

    # Server side
    async def create(self):
        pass

    # Client side
    async def open(self):
        pass

    async def close(self):
        await self._queue.put(None)

    # Any side
    async def send(self, task):
        return await self._remote_queue.put(self._protocol.encode(task))

    async def recv(self):
        try:
            bindata = await asyncio.wait_for(
                self._queue.get(), timeout=self._timeout
            )
            data = self._protocol.decode(bindata)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            return None
        return data
