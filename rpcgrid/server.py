import asyncio
from logging import getLogger
from timeit import default_timer as timer
import multiprocessing as mp
from threading import Thread

from rpcgrid.base import Base
from rpcgrid.task import State
from rpcgrid.providers.base import BaseProvider

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
    async def create(self, executor=None):
        await self._provider.create()
        # asyncio.ensure_future(self.run(), loop=self._loop)
        asyncio.ensure_future(self.response_loop(), loop=self._loop)
        asyncio.ensure_future(self.receive_loop(), loop=self._loop)
        self._executor = executor
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


class ExecuterServerProvider(BaseProvider, AsyncServer):
    _recv_queue: mp.Queue = None
    _server_pool: list = list
    _manager: mp.Manager = None
    _executors: list = list

    @staticmethod
    def initializer(self):
        print('Enter to initializer')
        loop = asyncio.get_event_loop()
        return AsyncServer(self, loop=loop).create()

    @staticmethod
    def executer(self):
        print('Enter to executer')
        server = ExecuterServerProvider.initializer(self)
        while self.running:
            data = self._recv_queue.get()
            print('RUNNN', data)
            pass

    async def receive_loop(self):
        while self.running:
            tasks = await self._provider.recv()
            if tasks is not None:
                for task in tasks:
                    task.time = timer()
                    print('Pull task to multyprocessing')
                    self._recv_queue.put(task)
                    # future = asyncio.Future()
                    # future.add_done_callback(self.push_response)
                    # asyncio.ensure_future(self.method_call(task, future))

    # Any side
    async def send(self, task):
        if not self.is_connected():
            raise ConnectionError(
                "Connection error between client server not establish"
            )
        print('send task!!!!!')
        # return await self._remote_queue.put(await self._protocol.encode(task))

    async def recv(self, timeout=None):
        print('recv task!!!!!')
        if not self.is_connected():
            raise ConnectionError(
                "Connection error between client server not establish"
            )
        try:

            data_raw = self._recv_queue.get(timeout=timeout)
            print(data_raw)
            data = await self._protocol.decode(data_raw)
            self._recv_queue.task_done()
            # log.info(data)
            return data

        except asyncio.TimeoutError:
            log.debug("Timeout for recv in local provider")
            return None

    async def create(self, executor=None, initializer=None, workers=4):
        # self._manager = mp.Manager()
        # self._response_queue = mp.Queue()
        self._recv_queue = mp.Queue()
        if executor == 'thread':
            from threading import Thread
            self._executors = [
                Thread(target=ExecuterServerProvider.executer, args=(self,)) for _ in range(workers)]
        for t in self._executors:
            t.start()

        await AsyncServer.create(self)

    async def close(self):
        await BaseProvider.close(self)
        for t in self._executors:
            t.join()
        log.info('close ExecuterServerProvider client')
