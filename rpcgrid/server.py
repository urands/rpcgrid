import asyncio
from logging import getLogger
from timeit import default_timer as timer

from rpcgrid.base import Base
from rpcgrid.task import State

log = getLogger(__name__)


class AsyncMethods:
    _methods = {}

    async def call(self, method, *args, **kwargs):
        if method in self._methods:
            if asyncio.iscoroutinefunction(self._methods[method]):
                return await self._methods[method](*args, **kwargs)
            else:
                return self._methods[method](*args, **kwargs)
        raise Exception(f'Method {method} not allowed')

    def add(self, name, func):
        if not callable(func):
            raise AttributeError(f"{name}:{func} not callable")
        self._methods[name] = func


class GlobalAsyncMethods(AsyncMethods):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Methods:
    _methods = {}

    def add(self, name, func):
        if not callable(func):
            raise AttributeError(f"{name}:{func} not callable")
        self._methods[name] = func

    def call(self, method, *args, **kwargs):
        if method in self._methods:
            return self._methods[method](*args, **kwargs)
        raise Exception(f'Method {method} not allowed')


class GlobalMethods(Methods):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class AsyncServer(Base):
    _response_queue: asyncio.Queue = asyncio.Queue()

    def create(self):
        self._provider.create()
        # asyncio.ensure_future(self.run(), loop=self._loop)
        asyncio.ensure_future(self.response_loop(), loop=self._loop)
        asyncio.ensure_future(self.receive_loop(), loop=self._loop)
        return self

    def push_response(self, future):
        self._response_queue.put_nowait(future.result())

    async def response_loop(self):
        while self.running:
            task = await self._response_queue.get()
            if task is not None:
                task.time = timer() - task.time
                await self.provider.send(task)

    async def receive_loop(self):
        while self.running:
            tasks = await self._provider.recv()
            if tasks is not None:
                for task in tasks:
                    task.time = timer()
                    future = asyncio.Future()
                    future.add_done_callback(self.push_response)
                    asyncio.ensure_future(self.method_call(task, future))

    async def method_call(self, task, future=None):
        methods = GlobalAsyncMethods()
        try:
            task.result = await methods.call(task.method, *task.params)
            task.status = State.COMPLETED
        except Exception as e:
            task.error = str(e)
            task.status = State.FAILED
            # if future is not None:
            #    future.set_exception(e)
        if future is not None:
            future.set_result(task)
        return task
