from rpcgrid.task import Task


class Client:
    _provider = None
    _method = None

    def __init__(self, provider):
        self._provider = provider
        self._provider.open(self.method_response)

    @property
    def provider(self):
        return self._provider

    def method_response(self, task):
        pass

    def __getattr__(self, item):
        if self._method is None:
            self._method = item
        else:
            self._method = '.'.join([self._method, item])
        return self

    def __call__(self, *args, **kwargs):
        if not self.provider.is_connected():
            raise ConnectionError(f'Connection lost. {self._provider}')
        task = Task().create(self._method, *args, **kwargs)
        self._method = None
        task = self.provider.call_method(task)
        # TODO: Call is blocking
        response = self.provider.recv()
        if response is not None:
            if task.id == response.id:
                task.result = response.result
                task.error = response.error
                task.status = response.status
                task.event.set()

                return task
        task.status = task.status.FAILED
        return task
