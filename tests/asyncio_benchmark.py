import asyncio
import time
from datetime import datetime

import rpcgrid.aio as rpcg
from rpcgrid.aio.providers.socket import SocketProvider


async def create_server(p=None):
    @rpcg.register
    async def sum(x, y):
        return x + y

    @rpcg.register
    async def sleep(x):
        print('start sleep:', x, datetime.now())
        await asyncio.sleep(x)
        print('stop', x, datetime.now())
        return x

    return await rpcg.create(p)


async def benchmark(rpcserver, rpcclient):
    print('Benchmark start server')
    print('Call sum:', await rpcclient.sum(5, 6).wait())

    rpf = 5454

    async def callback_task(task):
        print('Callback task', task.result, task.status, task.error, rpf)
        # await asyncio.sleep(3)
        # print('done call', task.result)

    t1 = rpcclient.sleep(10, parallel=False).callback(callback_task)
    t2 = rpcclient.sleep(2, parallel=False)
    t3 = rpcclient.sleep(1, parallel=False).callback(callback_task)

    '''
    for _ in range(5):
        print(t1.params, t1.status)
        print(t2.params, t2.status)
        print(t3.params, t3.status)
        await asyncio.sleep(1)
    '''
    print('Call sleep:', await t1.wait())
    print('Call sleep:', await t2.wait())
    print('Call sleep:', await t3.wait())

    start = datetime.now()
    n = 1000
    for i in range(n):
        c = await rpcclient.sum(i, i).wait()
        if c != 2 * i:
            print('Error:', c, ' true:', 2 * i)
    t = datetime.now() - start
    print(
        'profile time:',
        n,
        t,
        round(1000 * n / (t.microseconds + 0.001), 2),
        'it/ms',
    )

    print('Simple batch operation:')
    tsk = []
    start = datetime.now()
    for i in range(n):
        tsk.append(rpcclient.sum(i, i))
    t = datetime.now() - start
    print(
        'task created time:',
        n,
        t,
        round(n / (t.microseconds / 1000), 2),
        'it/ms',
    )

    for i in range(n):
        if (await tsk[i].wait()) != 2 * i:
            print('Error:', c, ' true:', 2 * i)
    t = datetime.now() - start
    print(
        'profile time:', n, t, round(n / (t.microseconds / 1000), 2), 'it/ms'
    )

    await rpcclient.close()
    await rpcserver.close()


async def main(loop):
    # Create RPC server
    socket_rpcserver = await create_server(SocketProvider(loop=loop))
    # Open server provider indirect
    socket_rpcclient = await rpcg.open(
        SocketProvider(connection='localhost:6300', loop=loop)
    )

    print('SOCKET TEST')
    t2 = socket_rpcclient.sleep(2, parallel=False)
    print(await t2.wait())
    # await benchmark(socket_rpcserver, socket_rpcclient)

    await socket_rpcserver.close()
    await socket_rpcclient.close()

    print('TCP Done')

    rpcserver = await create_server()
    rpcclient = await rpcg.open()

    # Cross connection for localprovider
    rpcserver.provider.set_remote_provider(rpcclient)
    rpcclient.provider.set_remote_provider(rpcserver)

    print('LOCAL TEST')
    await benchmark(rpcserver, rpcclient)

    print('Done')

    await rpcserver.close()
    await rpcclient.close()

    time.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    # print('FOREVER')
    # loop.run_forever()
