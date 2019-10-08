class BaseProvider:
    _request_callback = None
    _response_callback = None

    # TODO: add suppor custom middlewares

    def create(self, callback):
        raise NotImplementedError("Providers must implement this method")

    def open(self, callback):
        raise NotImplementedError("Providers must implement this method")

    def is_connected(self):
        raise NotImplementedError("Providers must implement this method")

    def send(self, task):
        raise NotImplementedError("Providers must implement this method")

    def recv(self):
        raise NotImplementedError("Providers must implement this method")

    def set_request_callback(self, callback):
        self._request_callback = callback

    def set_response_callback(self, callback):
        self._response_callback = callback

    def call_method(self, task):
        if self._response_callback is None:
            raise ConnectionError('Providers must be connected.')
        self.send(task)
        task.status = task.status.PENDING
        return task
