import queue

from rpcgrid.providers.base import BaseProvider


class LocalProvider(BaseProvider):
    _protocol = None
    _queue = None
    _remote_queue = None
    _timeout = None

    def __init__(self, protocol):
        self._protocol = protocol
        self._queue = queue.Queue()

    def is_connected(self):
        return True

    def set_remote_provider(self, remote):
        self._remote_queue = remote.provider._queue

    # Server side
    def create(self):
        pass

    # Client side
    def open(self):
        pass

    def close(self):
        self._queue.put(None)
        self._queue.join()

    # Any side
    def send(self, task):
        return self._remote_queue.put(self._protocol.encode(task))

    def recv(self):
        data = self._protocol.decode(self._queue.get(timeout=self._timeout))
        self._queue.task_done()
        return data
