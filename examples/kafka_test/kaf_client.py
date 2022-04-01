import asyncio
import logging
# from time import sleep
import time

import rpcgrid
# from rpcgrid.base import Base
# from rpcgrid.providers import SocketProvider
from rpcgrid.providers.kafka import KafkaProvider


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


async def worker(rpc):
    # First example
    print('First example')
    r = await rpc.sum(3,4)
    print("RPC SUM:", r)

    # Second example
    print('Second example')
    tasks = []
    for i in range(3):
        print(f'call sleep({i})')
        tsk = rpc.sleep(i)
        tasks.append(tsk)
    results = await asyncio.gather(*tasks)
    print('Result:', results)
    for t in tasks:
        print('Task profile:', t.time)
    # print('client:', tsk)
    await asyncio.sleep(1)

    await rpc.close()


async def main():
    client_provider = KafkaProvider('task_topic', bootstrap_servers='localhost:9091')
    rpcclient = await rpcgrid.client(client_provider)

    await worker(rpcclient)

if __name__ == '__main__':
    asyncio.run(main())
