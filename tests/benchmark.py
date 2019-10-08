import threading
import time
from datetime import datetime

import rpcgrid
from rpcgrid.providers.socket import SocketProvider


def create_server(p=None):
    @rpcgrid.register
    def sum(x, y):
        return x + y

    @rpcgrid.register
    def sleep(x):
        print('start sleep:', x, datetime.now())
        time.sleep(x)
        print('stop', x, datetime.now())
        return x

    return rpcgrid.create(p)


def benchmark(rpcserver, rpcclient):
    print('Benchmark start server')
    threading.Thread(target=rpcserver.run, daemon=False).start()
    time.sleep(0.1)
    print('Call sum:', rpcclient.sum(5, 6).wait())
    t1 = rpcclient.sleep(0.5)
    t2 = rpcclient.sleep(0.3)
    print('t1:', t1.wait())
    print('t2:', t2.wait())
    start = datetime.now()
    for i in range(50000):
        c = rpcclient.sum(i, i).wait()
        if c != 2 * i:
            print('Error:', c, ' true:', 2 * i)
    t = datetime.now() - start
    print('profile time:', t, 50000 / t.microseconds * 1000, 'it/ms')


if __name__ == '__main__':
    # Create RPC server
    socket_rpcserver = create_server(SocketProvider())
    # Open server provider indirect
    socket_rpcclient = rpcgrid.open(SocketProvider('localhost:6300'))

    print('SOCKET TEST')
    benchmark(socket_rpcserver, socket_rpcclient)

    rpcserver = create_server()
    rpcclient = rpcgrid.open()

    # Cross connection for localprovider
    rpcserver.provider.set_remote_provider(rpcclient)
    rpcclient.provider.set_remote_provider(rpcserver)

    print('LOCAL TEST')
    benchmark(rpcserver, rpcclient)

    print('Done')

    # time.sleep(1)
