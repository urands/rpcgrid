import asyncio
from logging import getLogger

import aiokafka.errors
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from rpcgrid.protocol.jsonrpc import JsonRPC
from rpcgrid.providers.base import BaseProvider

log = getLogger(__name__)


class KafkaProvider(BaseProvider):
    _protocol = None
    _server: bool = False

    def __init__(self, topic_name, *args, **kwargs):
        if 'protocol' in kwargs:
            self._protocol = kwargs['protocol']
        else:
            self._protocol = JsonRPC()
        self._topic_tasks = topic_name + '_tasks'
        self._topic_results = topic_name + '_results'
        self._kafka_config = kwargs

    def is_connected(self):
        # TODO: kafka ok
        return True

    # Server side
    async def create(self):
        self._server = True
        # bootstrap_servers='localhost:9091'
        self._kafka_producer = AIOKafkaProducer(**self._kafka_config)
        self._kafka_consumer = AIOKafkaConsumer(self._topic_tasks, **self._kafka_config)
        # Get cluster layout and initial topic/partition leadership information
        await self._kafka_producer.start()
        await self._kafka_consumer.start()


    # Client side
    async def open(self):
        self._server = False
        self._kafka_producer = AIOKafkaProducer(**self._kafka_config)
        self._kafka_consumer = AIOKafkaConsumer(self._topic_results, **self._kafka_config)
        # Get cluster layout and initial topic/partition leadership information
        await self._kafka_producer.start()
        await self._kafka_consumer.start()

    async def close(self):
        log.info('close local client')
        await self._kafka_producer.stop()
        await self._kafka_consumer.stop()
        log.info('close ok client')

    # Any side
    async def send(self, task):
        if not self.is_connected():
            raise ConnectionError(
                "Connection error between client server not establish"
            )
        
        data = await self._protocol.encode(task)
        if self._server:
            return await self._kafka_producer.send_and_wait(self._topic_results, data.encode())
        else:
            return await self._kafka_producer.send_and_wait(self._topic_tasks, data.encode())


    async def recv(self, timeout=None):
        if not self.is_connected():
            raise ConnectionError(
                "Connection error between client server not establish"
            )
        try:

            data_raw = await asyncio.wait_for(
                self._kafka_consumer.getone(),
                timeout=timeout,
            )
            # log.debug(data_raw)
            data = await self._protocol.decode(data_raw.value)
            # log.info(data)
            return data

        except asyncio.TimeoutError:
            log.warning("Timeout for recv kafka")
            return None
        except aiokafka.errors.ConsumerStoppedError:
            log.info("consumer stopped")
            return None

