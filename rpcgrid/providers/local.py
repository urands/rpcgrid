import queue

from rpcgrid.providers.base import BaseProvider


class LocalProvider(BaseProvider):
    _protocol = None
    _queue = None
    _remote_queue = None
    _timeout = 5
    _connected = False

    def __init__(self, protocol):
        self._protocol = protocol

    def is_connected(self):
        return self._connected

    def set_remote_provider(self, remote):
        self._remote_queue = remote.provider._queue

    # Server side
    def create(self, callback):
        self.set_request_callback(callback)
        self._queue = queue.Queue()

    # Client side
    def open(self, callback):
        self.set_response_callback(callback)
        self._connected = True
        self._queue = queue.Queue()

    # Any side
    def send(self, task):
        return self._remote_queue.put(self._protocol.encode(task))

    def recv(self):
        try:
            data = self._queue.get(timeout=self._timeout)
            if data is not None:
                return self._protocol.decode(data)
        except queue.Empty:
            return None
