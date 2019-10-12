import asyncio

import aio_pika
from rpcgrid.aio.providers.base import AsyncBaseProvider
from rpcgrid.protocol.jsonrpc import JsonRPC


async def process_e(message: aio_pika.IncomingMessage):
    async with message.process():
        print(message.body)
        await asyncio.sleep(1)


class RabbitProvider(AsyncBaseProvider):
    _protocol = None
    _queue = None
    _remote_queue = None
    _timeout = None
    _remote_queue_name = None
    _master_queue_name = None
    _loop = None
    _connection = False
    _rabbit = None
    _channel = None

    def __init__(
        self,
        connection='amqp://guest:guest@127.0.0.1/',
        master_queue=None,
        remote_queue=None,
        loop=None,
        protocol=JsonRPC(),
    ):
        self._protocol = protocol
        self._connection = connection
        self._remote_queue_name = remote_queue
        self._master_queue_name = master_queue
        self._loop = loop

    def is_connected(self):
        return True

    async def connect(self):
        self._rabbit = await aio_pika.connect(
            self._connection, loop=self._loop
        )

        self._queue = asyncio.Queue()

        # Creating channel
        self._channel = await self._rabbit.channel()

        # Declaring queue
        self._master_queue = await self._channel.declare_queue(
            self._master_queue_name
        )
        await self._master_queue.consume(self.process_message)

    # Server side
    async def create(self):
        if self._master_queue_name is None:
            self._master_queue_name = 'rpcgrid_server_queue'
        if self._remote_queue_name is None:
            self._remote_queue_name = 'rpcgrid_client_queue'
        await self.connect()

    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            await self._queue.put(message.body.decode())

    # Client side
    async def open(self):
        if self._master_queue_name is None:
            self._master_queue_name = 'rpcgrid_client_queue'
        if self._remote_queue_name is None:
            self._remote_queue_name = 'rpcgrid_server_queue'
        await self.connect()

    async def close(self):
        await self._rabbit.close()
        await self._queue.put(None)

    # Any side
    async def send(self, task):
        msg = self._protocol.encode(task)
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=msg.encode()),
            routing_key=self._remote_queue_name,
        )

    async def recv(self):
        try:
            bindata = await asyncio.wait_for(
                self._queue.get(), timeout=self._timeout
            )
            data = self._protocol.decode(bindata)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            return None
        return data
