import threading

import rpcgrid
from rpcgrid.providers.socket import SocketProvider


def create_server(p=None):
    @rpcgrid.register
    def sum(x, y):
        return x + y

    return rpcgrid.create(p)


def test_socket():
    rpcserver = create_server(SocketProvider())
    rpcclient = rpcgrid.open(SocketProvider('localhost:6300'))
    threading.Thread(target=rpcserver.run, daemon=False).start()
    assert rpcclient.sum(2, 3) == 5
