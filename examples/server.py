import rpcgrid as rpcg
from rpcgrid.providers import SocketProvider


@rpcg.register
def sum(x, y):
    return x + y


# Create RPC TCP server on port 1234
rpcserver = rpcg.create(SocketProvider(port=1234))
rpcserver.run()
