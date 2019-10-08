import asyncio
import time
from datetime import datetime

import rpcgrid.aio as rpcg

# from rpcgrid.aio.providers.socket import SocketProvider


async def create_server(p=None):
    @rpcg.register
    async def sum(x, y):
        return x + y

    @rpcg.register
    async def sleep(x):
        print('start sleep:', x, datetime.now())
        time.sleep(x)
        print('stop', x, datetime.now())
        return x

    return await rpcg.create(p)


async def benchmark(rpcserver, rpcclient):
    print('Benchmark start server')
    print('Call sum:', await rpcclient.sum(5, 6).wait())

    start = datetime.now()
    n = 100000
    for i in range(n):
        c = await rpcclient.sum(i, i).wait()
        if c != 2 * i:
            print('Error:', c, ' true:', 2 * i)
    t = datetime.now() - start
    print('profile time:', n, t, round(n / (t.microseconds/1000), 2), 'it/ms')

    print('Simple batch operation:')
    tsk = []
    start = datetime.now()
    for i in range(n):
        tsk.append(rpcclient.sum(i, i))
    t = datetime.now() - start
    print('task created time:', n, t,
          round(n / (t.microseconds/1000), 2), 'it/ms')

    for i in range(n):
        if (await tsk[i].wait()) != 2 * i:
            print('Error:', c, ' true:', 2 * i)
    t = datetime.now() - start
    print('profile time:', n, t, round(n / (t.microseconds/1000), 2), 'it/ms')

    await rpcclient.close()
    await rpcserver.close()


async def main(loop):
    # Create RPC server
    # socket_rpcserver = create_server(SocketProvider())
    # Open server provider indirect
    # socket_rpcclient = await rpcg.open(SocketProvider('localhost:6300'))

    print('SOCKET TEST')
    # await benchmark(socket_rpcserver, socket_rpcclient)

    rpcserver = await create_server()
    rpcclient = await rpcg.open()

    # Cross connection for localprovider
    rpcserver.provider.set_remote_provider(rpcclient)
    rpcclient.provider.set_remote_provider(rpcserver)

    print('LOCAL TEST')
    await benchmark(rpcserver, rpcclient)

    print('Done')

    time.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
