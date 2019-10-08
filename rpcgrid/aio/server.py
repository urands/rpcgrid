import asyncio

from rpcgrid.server import GlobalMethods, Methods, Server


class AsyncMethods(Methods):
    async def call(self, method, *args, **kwargs):
        if method in self._methods:
            return await self._methods[method](*args, **kwargs)
        raise Exception(f'Method {method} not allowed')


class GlobalAsyncMethods(AsyncMethods):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class AsyncServer(Server):
    _loop = None
    _response_queue = asyncio.Queue()

    def __init__(self, provider, loop=None):
        self._provider = provider
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

    async def create(self):
        await self._provider.create()
        asyncio.ensure_future(self.run(), loop=self._loop)
        asyncio.ensure_future(self.response_loop(), loop=self._loop)
        return self

    async def close(self):
        self._running = False
        await self._provider.close()
        await self._response_queue.put(None)

    @property
    def provider(self):
        return self._provider

    async def response_loop(self):
        while (self._running):
            task = await self._response_queue.get()
            if task is not None:
                await self.provider.send(task)

    def push_response(self, future):
        self._response_queue.put_nowait(future.result())

    async def run(self):
        while (self._running):
            tasks = await self._provider.recv()
            if tasks is not None:
                for task in tasks:
                    if task._parallel:
                        future = asyncio.Future()
                        future.add_done_callback(self.push_response)
                        asyncio.ensure_future(self.method_call(task, future))
                    else:
                        response = await self.method_call(task)
                        await self.provider.send(response)
        return

    async def method_call(self, task, future=None):
        methods = GlobalMethods()
        try:
            task.result = await methods.call(task.method, *task.params)

        except Exception as e:
            task.error = str(e)
        finally:
            task.method = None
        if future is not None:
            future.set_result(task)
        return task
