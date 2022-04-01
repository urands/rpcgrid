import asyncio
from logging import getLogger


from rpcgrid.protocol.jsonrpc import JsonRPC
from rpcgrid.providers.base import BaseProvider

log = getLogger(__name__)


class LocalProvider(BaseProvider):
    _protocol = None
    _queue: asyncio.Queue = None
    _remote_queue: asyncio.Queue = None

    def __init__(self, remote=None, protocol=JsonRPC(), loop=None):
        self._protocol = protocol
        self._queue = asyncio.Queue()
        if remote is not None:
            self.set_remote_provider(remote)

    def is_connected(self):
        return self._remote_queue is not None

    def set_remote_provider(self, remote):
        self._remote_queue = remote.get_queue()
        remote._remote_queue = self._queue

    # Server side
    async def create(self):

        self.is_connected()
        pass

    # Client side
    async def open(self):
        # self._queue = asyncio.Queue()
        pass

    async def close(self):
        log.info('close local client')
        # if self._remote_queue is not None:
        #    self._remote_queue.put(None)
        #    self._remote_queue = None
        # self._queue.put(None)
        await self._queue.join()
        log.info('close ok client')

    # Any side
    async def send(self, task):
        if not self.is_connected():
            raise ConnectionError(
                "Connection error between client server not establish"
            )

        return await self._remote_queue.put(await self._protocol.encode(task))

    async def recv(self, timeout=None):
        if not self.is_connected():
            raise ConnectionError(
                "Connection error between client server not establish"
            )
        try:

            data_raw = await asyncio.wait_for(
                asyncio.gather(self._queue.get()),
                timeout=timeout,
            )
            self._queue.task_done()
            data = await self._protocol.decode(data_raw)
            log.info(data)
            return data

        except asyncio.TimeoutError:
            log.debug("Timeout for recv in local provider")
            return None

    def get_queue(self) -> asyncio.Queue:
        return self._queue
