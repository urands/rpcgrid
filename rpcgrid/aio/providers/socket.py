import asyncio

from rpcgrid.aio.providers.base import AsyncBaseProvider
from rpcgrid.protocol.jsonrpc import JsonRPC


class SocketProvider(AsyncBaseProvider):
    _protocol = None
    _socket = None
    _clientsocket = None
    _timeout = 5
    _connected = False
    _server = None
    _loop = None
    _reader = None

    def __init__(
        self, connection=None, port=6300, loop=None, protocol=JsonRPC()
    ):
        self._protocol = protocol
        self.connection = connection
        self._port = port
        self._loop = loop

    def is_connected(self):
        return self._connected

    # Server side
    async def create(self):
        self._server = await asyncio.start_server(
            self.accept, 'localhost', self._port, loop=self._loop
        )
        asyncio.ensure_future(self._server.serve_forever(), loop=self._loop)
        # addr = self._server.sockets[0].getsockname()
        # print(f'Serving on {addr}')
        self._connected = True
        self._clientsocket = None

    # Client side
    async def open(self):
        # self.set_response_callback(callback)
        self.connection = self.connection.split(':')
        self.connection = (self.connection[0], int(self.connection[1]))
        self._reader, self._writer = await asyncio.open_connection(
            self.connection[0], self.connection[1], loop=self._loop
        )
        self._connected = True

    async def accept(self, reader, writer):
        self._reader = reader
        self._writer = writer
        # print('accept', reader, writer)

    # Any side
    async def send(self, task):
        data = self._protocol.encode(task)
        if self._writer is not None:
            self._writer.write(data.encode())

    async def close(self):
        if self._writer is not None:
            self._writer.close()
            self._writer = None

    async def recv(self):
        if not self.is_connected():
            raise ConnectionError(f'{self.connection} connection error')
        # SERVER
        data = None
        if self._reader is not None:
            data = await self._reader.read(124000)
        else:
            await asyncio.sleep(1)
            return

        if data is None or len(data) == 0:
            if self._server is not None:
                self._reader = None
                self._writer = None
            return None
        data = data.decode()

        if len(data) > 5 and data[0] == '{' and data[-1] == '}':
            data = list(map(lambda x: '{' + x + '}', data[1:-1].split('}{')))
        else:
            data = [data]

        return self._protocol.decode(data)
