import rpcgrid as rpcg
from rpcgrid.providers import SocketProvider

# Open connection with server
rpc = rpcg.open(SocketProvider('localhost:1234'))

# Call RPC sum  and wait results
print('2 + 3 = ', rpc.sum(2, 3).wait())

# Call RPC with callback on done
task = rpc.sum(1, 2)
# do something... (task execute parallel)
task.wait(10)  # Wait no more 10 seconds for results
print('1 + 2 = ', task.result if task.success else task.error)

# Call RPC wit callback
rpc.sum(1, 2).done(
    lambda tsk: print('1 + 2 =', tsk.result if tsk.success else tsk.error)
)
