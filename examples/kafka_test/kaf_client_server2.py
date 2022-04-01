import asyncio
import logging
import rpcgrid
from rpcgrid.providers.kafka import KafkaProvider

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

rpcclient = None

@rpcgrid.register
async def sum(x: int, y: int) -> str:
    global rpcclient
    print(f'CALL RPC SUM({x},{y})')
    r = await rpcclient.sleep(2)
    return f'sum+rpc sleep call : {r} , result:{r}'


async def main(loop):
    global rpcclient
    server_provider = KafkaProvider('task_topic_other', bootstrap_servers='localhost:9091')
    rpc = await rpcgrid.server(server_provider, loop=loop)

    client_provider = KafkaProvider('task_topic', bootstrap_servers='localhost:9091')
    rpcclient = await rpcgrid.client(client_provider)

    r = await rpcclient.sum(2, 3).wait(1000)

    print('Sum:', r)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()
