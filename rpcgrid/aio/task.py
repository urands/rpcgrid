import asyncio
from uuid import uuid4

from rpcgrid.task import State, Task


class AsyncTask(Task):

    def create(self, method, *args, **kwargs):
        self.id = str(uuid4())
        self.method = method
        self.params = args
        self.named_params = kwargs
        self.event = asyncio.Event()
        self.status = State.PENDING
        return self

    async def wait(self, timeout=5):
        try:
            await asyncio.wait_for(self.event.wait(),
                                   timeout=timeout)
            self.event.clear()
            self.status = State.COMPLETED
        except (asyncio.CancelledError, asyncio.TimeoutError):
            self.status = State.TIMEOUT
        return self.result
