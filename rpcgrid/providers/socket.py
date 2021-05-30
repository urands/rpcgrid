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

    def is_connected(self):
        return self._connected

    # Server side
    def create(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('localhost', self._port))
        self._socket.listen()
        self._connected = True
        self._clientsocket = None

    # Client side
    def open(self):
        # self.set_response_callback(callback)
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

    def close(self):
        if self._clientsocket is not None:
            self._clientsocket.close()
            self._clientsocket = None

        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def recv(self):
        if not self.is_connected():
            raise ConnectionError(f'{self.connection} connection error')
        try:
            if self._socket and self._clientsocket is None:
                self._clientsocket, addr = self._socket.accept()
            data = self._clientsocket.recv(24000).decode()

            # if len(data)>2 and data[0] == '{' and data[-1] == '}':
            #    data = list(
            #        map(lambda x: '{' + x + '}', data[1:-1].split('}{'))
            #    )
            # print(data)
        except ConnectionError:
            return None

        if data is None:
            self._clientsocket = None
            return None
        return self._protocol.decode(data)
