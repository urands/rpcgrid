import asyncio
import logging

# import os
import threading

import rpcgrid
import rpcgrid as rpcg

# from rpcgrid.base import Base
# from rpcgrid.providers import SocketProvider
from rpcgrid.providers.local import LocalProvider

# from time import sleep

# from rpcgrid.providers.socket import SocketProvider


def create_server(p=None):
    @rpcgrid.register
    def sum(x, y):
        print('x+y=', x, y, x + y)
        return x + y

    return rpcgrid.create(p)


def test_socket():

    server_provider = LocalProvider()
    rpcserver = create_server(server_provider)
    server = threading.Thread(target=rpcserver.run, daemon=False)
    server.start()
    client_provider = LocalProvider(server_provider)
    # rpcclient = rpcgrid.open(SocketProvider('localhost:6300'))
    rpcclient = rpcgrid.open(client_provider)
    task = rpcclient.sum(2, 3)
    print(task)
    print('Wait result:, ', task.wait())
    # assert rpcclient.sum(2, 3) == 5
    print('rpcclient cllose')
    rpcclient.close()
    print('rpcserver cllose')
    rpcserver.close()
    print('app join')
    server.join()
    print('app done')


@rpcg.register
async def sum(x, y):
    # sleep(3)
    # await asyncio.sleep(3)
    return x + y


logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


async def worker(rpcclient):
    for i in range(1):

        # Sleep for the "sleep_for" seconds.
        # print('worker loop')

        tsk = rpcclient.sum(3, i).callback(lambda r: print('done:', r))

        print('Result:', await tsk.wait(10))

        print('client:', tsk)

        # await asyncio.sleep(3)


def test_server():

    loop = asyncio.get_event_loop()

    server_provider = LocalProvider()
    rpcserver = rpcgrid.create(server_provider, loop)

    client_provider = LocalProvider(server_provider)

    # rpcclient = rpcgrid.open(SocketProvider('localhost:6300'))
    rpcclient = rpcgrid.open(client_provider, loop)

    asyncio.ensure_future(worker(rpcclient), loop=loop)

    rpcserver.run()


test_server()
