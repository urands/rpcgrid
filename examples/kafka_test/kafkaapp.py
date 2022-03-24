import asyncio
import logging
# from time import sleep
import time

import rpcgrid
# from rpcgrid.base import Base
# from rpcgrid.providers import SocketProvider
from rpcgrid.providers.kafka import KafkaProvider


# import os
# from rpcgrid.providers.thread import ThreadProvider
# from rpcgrid.providers.socket import SocketProvider

@rpcgrid.register
async def sum(x, y):
    # sleep(3)
    await asyncio.sleep(1)
    return x + y


@rpcgrid.register
async def sleep(x: int) -> str:
    # sleep(3)
    #time.sleep(x)
    await asyncio.sleep(1)
    print('complete:', x)
    return f'sleep:{x} done'


logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


async def worker(rpcclient):
    tasks = []
    for i in range(3):
        # Sleep for the "sleep_for" seconds.
        print('worker loop')
        tsk = rpcclient.sleep(i)
        #print('Result await:', await tsk)
        tasks.append(tsk)
    results = await asyncio.gather(*tasks)
    # results = [await t.wait(3) for t in tasks]
    print('Result:', results)
    for t in tasks:
        print('Task profile:', t.time)
    # print('client:', tsk)
    await asyncio.sleep(1)


async def create_connection():
    # loop = asyncio.get_event_loop()
    loop = None
    server_provider = KafkaProvider('task_topic', bootstrap_servers='localhost:9091')
    client_provider = KafkaProvider('task_topic', bootstrap_servers='localhost:9091')
    rpcserver = await rpcgrid.server(server_provider, loop=loop, executor=None)
    rpcclient = await rpcgrid.client(client_provider, loop=loop)
    return rpcserver, rpcclient


async def main():
    rpcserver, rpcclient = await create_connection()
    await worker(rpcclient)
    # await asyncio.sleep(2)


if __name__ == '__main__':
    asyncio.run(main())
