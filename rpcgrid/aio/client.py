import asyncio

from rpcgrid.aio.task import AsyncTask
from rpcgrid.client import Client


class AsyncClient(Client):
    _provider = None
    _method = None
    _requests = {}
    _running = True
    _request_queue = asyncio.Queue()
    _loop = None

    def __init__(self, provider, loop=None):
        self._provider = provider
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

    async def open(self):
        await self._provider.open()
        asyncio.ensure_future(self.request_loop(), loop=self._loop)
        asyncio.ensure_future(self.run(), loop=self._loop)
        return self

    async def close(self):
        self._running = False
        await self._provider.close()
        await self._request_queue.put(None)

    async def request_loop(self):
        while(self._running):
            task = await self._request_queue.get()
            if task is not None:
                await self.provider.call_method(task)
            if self._request_queue.empty():
                self._request_queue.task_done()

    async def run(self):
        while(self._running):
            responses = await self._provider.recv()
            if responses is not None:
                for response in responses:
                    if response.id in self._requests:
                        task = self._requests[response.id]
                        task.result = response.result
                        task.error = response.error
                        task.status = response.status
                        task.event.set()
                        del self._requests[response.id]

    def __call__(self, *args, **kwargs):
        if not self.provider.is_connected():
            self._provider.open()
            if not self.provider.is_connected():
                raise ConnectionError(f'Connection lost. {self._provider}')
        task = AsyncTask().create(self._method, *args, **kwargs)
        self._method = None
        self._requests[task.id] = task
        self._request_queue.put_nowait(task)
        return task
