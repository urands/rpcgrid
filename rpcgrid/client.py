import threading
import time

from rpcgrid.task import Task


class Client:
    _provider = None
    _method = None
    _requests = {}
    _running = True

    def __init__(self, provider):
        self._provider = provider

    def open(self):
        self._provider.open()
        threading.Thread(target=self.run, daemon=False).start()
        return self

    def close(self):
        self._running = False
        self._provider.close()

    @property
    def provider(self):
        return self._provider

    def method_response(self, task):
        pass

    def run(self):
        while threading.main_thread().is_alive() and self._running:
            responses = self.provider.recv()
            if responses is not None:
                for response in responses:
                    if response.id in self._requests:
                        task = self._requests[response.id]
                        task.result = response.result
                        task.error = response.error
                        task.status = response.status
                        task.event.set()
                        del self._requests[response.id]
            else:
                time.sleep(0.1)

    def __getattr__(self, item):
        if self._method is None:
            self._method = item
        else:
            self._method = '.'.join([self._method, item])
        return self

    def __call__(self, *args, **kwargs):
        if not self.provider.is_connected():
            self._provider.open()
            if not self.provider.is_connected():
                raise ConnectionError(f'Connection lost. {self._provider}')
        task = Task().create(self._method, *args, **kwargs)
        self._method = None
        self._requests[task.id] = task
        return self.provider.call_method(task)
