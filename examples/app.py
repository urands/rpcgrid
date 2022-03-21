import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
# import os
import threading

import rpcgrid
import rpcgrid as rpcg

# from rpcgrid.base import Base
# from rpcgrid.providers import SocketProvider
from rpcgrid.providers import LocalProvider
from rpcgrid.providers.thread import ThreadProvider

# from time import sleep
import time
# from rpcgrid.providers.socket import SocketProvider

@rpcg.register
async def sum(x, y):
    # sleep(3)
    await asyncio.sleep(1)
    return x + y


@rpcg.register
async def sleep(x: int) -> str:
    # sleep(3)
    time.sleep(x)
    #await asyncio.sleep(1)
    print('complete:', x)
    return f'sleep:{x} done'


logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


async def worker(rpcclient):

    tasks = []
    for i in range(3):
        # Sleep for the "sleep_for" seconds.
        print('worker loop')
        tsk = rpcclient.sleep(i).wait(10)
        tasks.append(tsk)
    results = await asyncio.gather(*tasks)
    #results = [await t.wait(3) for t in tasks]
    print('Result:', results)
        # print('client:', tsk)
    await asyncio.sleep(1)

async def create_connection():
    loop = asyncio.get_event_loop()
    server_provider = LocalProvider()
    rpcserver = await rpcgrid.create(server_provider, loop=loop, executor= None)

    client_provider = LocalProvider(server_provider)

    # rpcclient = rpcgrid.open(SocketProvider('localhost:6300'))
    rpcclient = await rpcgrid.open(client_provider, loop=loop)

    # asyncio.ensure_future(worker(rpcclient), loop=loop)

    return rpcserver, rpcclient


async def main():
    rpcserver, rpcclient = await create_connection();

    await worker(rpcclient)

    #await asyncio.sleep(2)


asyncio.run(main())
