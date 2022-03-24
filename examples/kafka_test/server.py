import rpcgrid as rpcg
import asyncio
from rpcgrid.providers import SocketProvider, LocalProvider
# from kafka import KafkaConsumer
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

@rpcg.register
async def sum(x: int, y: int ) -> int:
    return x + y

async def send_one():
    producer = AIOKafkaProducer(bootstrap_servers='localhost:9091')
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # Produce message
        await producer.send_and_wait("my_topic", b"Super message")
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()

async def consume():
    consumer = AIOKafkaConsumer(
        'my_topic', 'my_other_topic',
        bootstrap_servers='localhost:9091',
        group_id="my-group")
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

async def main():
    # rpcserver = await rpcg.server(SocketProvider(port=1234))
    # rpcserver._loop.run_forever()

    await send_one()
    await consume()
    #consumer = KafkaConsumer(bootstrap_servers='localhost:9091')
    #for msg in consumer:
    #    print(msg)

# Create RPC TCP server on port 1234

if __name__ == '__main__':
    print('Start server')
    asyncio.run(main())


