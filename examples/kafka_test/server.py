import asyncio
import logging
import rpcgrid
from rpcgrid.providers.kafka import KafkaProvider

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

@rpcgrid.register
async def sum(x, y):
    return x + y


@rpcgrid.register
async def sleep(x: int) -> str:
    print(f'CALL RPC SLEEP({x})')
    await asyncio.sleep(x)
    return f'sleep:{x} done'


async def main(loop):
    server_provider = KafkaProvider('task_topic', bootstrap_servers='localhost:9091')
    rpc = await rpcgrid.server(server_provider, loop = loop)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()
