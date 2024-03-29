import threading
from enum import IntEnum, auto
from uuid import uuid4


class State(IntEnum):
    COMPLETED = 0
    CREATED = auto()
    PENDING = auto()
    RUNNING = auto()
    FAILED = auto()
    TIMEOUT = auto()


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
