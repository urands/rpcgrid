import asyncio
import threading
from enum import IntEnum, auto
from timeit import default_timer as timer
from uuid import uuid4


class State(IntEnum):
    COMPLETED = 0
    CREATED = auto()
    PENDING = auto()
    RUNNING = auto()
    FAILED = auto()
    TIMEOUT = auto()


class AsyncTask():  #

    id = None
    method = None
    result = None
    params = None
    event = None
    named_params = None
    status = State.CREATED
    error = None
    _parallel = True
    _callback = None
    time = None

    def __init__(self, timeout=None):
        self._timeout = timeout
        # coro = self.wait()
        # super().__init__(coro)

    def create(self, method, *args, **kwargs):
        self.id = str(uuid4())
        self.method = method
        self.params = args
        self.named_params = kwargs
        self.event = asyncio.Event()
        self.status = State.PENDING
        self.time = timer()
        # self.task = asyncio.create_task(self.wait(None))

        return self

    async def wait(self, timeout=None):
        try:
            await asyncio.wait_for(self.event.wait(), timeout=timeout)
            self.event.clear()
        except (asyncio.CancelledError, asyncio.TimeoutError) as error:
            self.status = State.TIMEOUT
            if self._callback is not None:
                asyncio.ensure_future(self._callback(self))
            raise error
        return self.result

    @property
    def pending(self):
        return self.status == State.PENDING

    @property
    def success(self):
        return self.status == State.COMPLETED

    @property
    def done(self):
        return self.status in [State.COMPLETED, State.FAILED, State.TIMEOUT]

    def callback(self, fn):
        self._callback = fn
        return self

    def __await__(self, *args, **kwargs):
        # print('__await__')
        return self.wait(timeout=self._timeout).__await__()

    def __repr__(self):
        return (
            f'AsyncTask #{self.id} : {self.method} {self.params} '
            f'{self.named_params} Result: {self.result} '
            f'Error: {self.error} status: {self.status} '
            f'Time: {self.time}'
        )

    def __call__(self, *args, **kwargs):
        return self.wait(**kwargs)


class Task:
    '''
    Class task return state
    '''

    id = None
    method = None
    result = None
    params = None
    named_params = None
    status = State.CREATED
    error = None
    _parallel = True
    _callback = None

    @property
    def pending(self):
        return self.status == State.PENDING

    @property
    def success(self):
        return self.status == State.COMPLETED

    @property
    def done(self):
        return self.status in [State.COMPLETED, State.FAILED, State.TIMEOUT]

    def create(self, method, *args, **kwargs):
        self.id = str(uuid4())
        self.method = method
        self.params = args
        self.named_params = kwargs
        self.event = threading.Event()
        self.status = State.PENDING
        return self

    def callback(self, fn):
        self._callback = fn
        return self

    def wait(self, timeout=10):
        if (self.event.wait(timeout=timeout)) is True:
            self.event.clear()
            return self.result
        self.status = State.TIMEOUT
        return self.result

    def __repr__(self):
        return (
            f'Task #{self.id} : {self.method} {self.params} '
            f'{self.named_params} Result: {self.result} '
            f'Error: {self.error} status: {self.status}'
        )
