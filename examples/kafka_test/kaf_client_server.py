import asyncio
import logging
import rpcgrid
from rpcgrid.providers.kafka import KafkaProvider

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

@rpcgrid.register
async def sleep(x: int) -> str:
    print(f'CALL RPC SLEEP({x})')
    await asyncio.sleep(1)
    return f'sleep:{x} done'


async def main(loop):
    server_provider = KafkaProvider('task_topic', bootstrap_servers='localhost:9091')
    rpc = await rpcgrid.server(server_provider, loop = loop)

    client_provider = KafkaProvider('task_topic_other', bootstrap_servers='localhost:9091')
    rpcclient = await rpcgrid.client(client_provider)

    r = await rpcclient.sum(2,3)

    print('Sum:', r)




if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()
