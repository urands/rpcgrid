import asyncio

import rpcgrid as rpcg
from rpcgrid.providers import SocketProvider


async def main():
    # Open connection with server
    rpc = await rpcg.open(SocketProvider('localhost:1234'))
    # Call RPC sum  and wait results
    # print('2 + 3 = ', await rpc.sum(2, 3).wait())

    # Call RPC with callback on done
    task = rpc.sum(1, 2)
    # do something... (task execute parallel)
    await task.wait(1)  # Wait no more 10 seconds for results
    print('1 + 2 = ', task.result if task.success else task.error)

    # Call RPC wit callback
    rpc.sum(1, 2).done(
        lambda tsk: print('1 + 2 =', tsk.result if tsk.success else tsk.error)
    )


if __name__ == '__main__':
    asyncio.run(main(), debug=False)
