import asyncio
from timeit import default_timer as timer

from rpcgrid.task import AsyncTask, State


class AsyncClient:
    _provider = None
    _method = None
    _requests: dict = {}
    _running = True
    _request_queue: asyncio.Queue = None
    _loop = None

    def __init__(self, provider, loop=None):
        self._provider = provider
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

    async def open(self):
        await self._provider.open()
        self._request_queue = asyncio.Queue()
        asyncio.ensure_future(self.request_loop(), loop=self._loop)
        asyncio.ensure_future(self.response_loop(), loop=self._loop)
        return self

        # await self._request_queue.put(None)

    async def request_loop(self):
        while self._running:
            task = await self._request_queue.get()
            if task is not None:
                await self._provider.call_method(task)
                task.status = State.RUNNING
            self._request_queue.task_done()
            # if self._request_queue.empty():

    async def response_loop(self):
        while self._running:
            responses = await self._provider.recv()
            if responses is not None:
                for response in responses:
                    if response.id in self._requests:
                        task = self._requests[response.id]
                        del self._requests[response.id]
                        task.result = response.result
                        task.error = response.error
                        if task.error is None:
                            task.status = State.COMPLETED
                        else:
                            task.status = State.FAILED

                        task.time = timer() - task.time
                        task.event.set()
                        if task._callback is not None:
                            if asyncio.iscoroutinefunction(task._callback):
                                asyncio.ensure_future(
                                    task.callback(task), loop=self._loop
                                )
                            else:
                                task._callback(task)

    def __getattr__(self, item):
        if self._method is None:
            self._method = item
        else:
            self._method = '.'.join([self._method, item])
        return self

    def __call__(self, *args, **kwargs):

        # log.debug('call client:', self._method, args, kwargs)
        if not self._provider.is_connected():
            raise ConnectionError(f'Connection lost. {self._provider}')

        task = AsyncTask().create(self._method, *args, **kwargs)
        self._method = None
        task.status = State.PENDING
        self._requests[task.id] = task
        self._request_queue.put_nowait(self._requests[task.id])
        return self._requests[task.id]
