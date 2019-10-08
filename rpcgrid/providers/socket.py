import socket

from rpcgrid.protocol.jsonrpc import JsonRPC
from rpcgrid.providers.base import BaseProvider


class SocketProvider(BaseProvider):
    _protocol = None
    _socket = None
    _clientsocket = None
    _timeout = 5
    _connected = False

    def __init__(self, connection=None, port=6300, protocol=JsonRPC()):
        self._protocol = protocol
        self.connection = connection
        self._port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def is_connected(self):
        return self._connected

    # Server side
    def create(self, callback):
        self.set_request_callback(callback)
        self.socket.bind(('localhost', self._port))
        self.socket.listen()
        self.connected = True
        self._clientsocket = None

    # Client side
    def open(self, callback):
        self.set_response_callback(callback)
        self.connection = self.connection.split(':')
        self.connection = (self.connection[0], int(self.connection[1]))
        self._clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._clientsocket.connect(self.connection)
        self._connected = True

    # Any side
    def send(self, task):
        if self._clientsocket is not None:
            data = self._protocol.encode(task)
            self._clientsocket.send(data.encode())

    def recv(self):
        if self._clientsocket is None:
            try:
                self.socket.settimeout(1)
                self._clientsocket, addr = self.socket.accept()
            except socket.timeout:
                return None
        data = self._clientsocket.recv(8048)
        if data is None:
            self._clientsocket = None
            return None
        return self._protocol.decode(data.decode())
