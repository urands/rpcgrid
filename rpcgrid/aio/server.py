import asyncio
import threading

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

    def __init__(self, provider, loop=None):
        self._provider = provider
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

    async def create(self):
        await self._provider.create()
        asyncio.ensure_future(self.run(), loop=self._loop)
        return self

    async def close(self):
        self._running = False
        await self._provider.close()

    @property
    def provider(self):
        return self._provider

    async def run(self):
        while (self._running):
            tasks = await self._provider.recv()
            if tasks is not None:
                for task in tasks:
                    response = await self.method_call(task)
                    await self.provider.send(response)
        return

        while threading.main_thread().is_alive() and self._running:
            tasks = self._provider.recv()
            if tasks is not None:
                for task in tasks:
                    response = self.method_call(task)
                    self.provider.send(response)

    async def method_call(self, task):
        methods = GlobalMethods()
        try:
            task.result = await methods.call(task.method, *task.params)
        except Exception as e:
            task.error = str(e)
        finally:
            task.method = None
        return task
