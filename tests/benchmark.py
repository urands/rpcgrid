import threading
import time
from datetime import datetime

import rpcgrid as rpcg
from rpcgrid.providers.socket import SocketProvider


def create_server(p=None):
    @rpcg.register
    def sum(x, y):
        return x + y

    @rpcg.register
    def sleep(x):
        print('start sleep:', x, datetime.now())
        time.sleep(x)
        print('stop', x, datetime.now())
        return x

    return rpcg.create(p)


def benchmark(rpcserver, rpcclient):
    print('Benchmark start server')
    threading.Thread(target=rpcserver.run, daemon=False).start()
    time.sleep(0.1)
    print('Call sum:', rpcclient.sum(5, 6).wait())
    start = datetime.now()
    n = 1000
    for i in range(n):
        c = rpcclient.sum(i, i).wait()
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
        if tsk[i].wait() != 2 * i:
            print('Error:', c, ' true:', 2 * i)
    t = datetime.now() - start
    print('profile time:', n, t, round(n / (t.microseconds/1000), 2), 'it/ms')

    rpcclient.close()
    rpcserver.close()


if __name__ == '__main__':
    # Create RPC server
    socket_rpcserver = create_server(SocketProvider())
    # Open server provider indirect
    socket_rpcclient = rpcg.open(SocketProvider('localhost:6300'))

    print('SOCKET TEST')
    benchmark(socket_rpcserver, socket_rpcclient)

    rpcserver = create_server()
    rpcclient = rpcg.open()

    # Cross connection for localprovider
    rpcserver.provider.set_remote_provider(rpcclient)
    rpcclient.provider.set_remote_provider(rpcserver)

    print('LOCAL TEST')
    benchmark(rpcserver, rpcclient)

    print('Done')

    time.sleep(1)
