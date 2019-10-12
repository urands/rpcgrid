# RPCGrid

Remote procedure call package for any protocol and any transport layer.
## Quickstart
#### Installation
```shell script
pip install rpcgrid
```
#### Server side
```python
import rpcgrid as rpcg
from rpcgrid.providers import SocketProvider

@rpcg.register
def sum(x, y): 
    return x + y

# Create RPC TCP server on port 1234
rpcserver = rpcg.create(SocketProvider(port = 1234))
rpcserver.run()
```

#### Client side

```python
import rpcgrid as rpcg
from rpcgrid.providers import SocketProvider

# Open connection with server  
rpc = rpcg.open(SocketProvider('localhost:1234'))

# Call RPC sum  and wait results
print('2 + 3 = ', rpc.sum(2,3).wait())

# Call RPC with callback on done 
task = rpc.sum(1, 2)
# do something... (task execute parallel)
task.wait(10) # Wait no more 10 seconds for results
print('1 + 2 = ', task.result if task.success else task.error)

# Call RPC wit callback
rpc.sum(1, 2).done(lambda tsk: print('1 + 2 =', tsk.result))
```


## Features
+ async/await support
+ logging remote procedure call
+ server/client side remote procedure call
+ custom transport and protocols
+ block/non-block call
+ parallel rpc calls in async mode

#### Protocol
+ JsonRPC protocol support


#### Transport
+ Single/Multithreading remote procedure call
+ UDP/TCP socket remote procedure call 
+ RabbitMQ remote procedure call


## Future plans
+ debug/trace remote procedure call
+ metric support (GraphQL, InfluxDB)
+ celery support
+ batch rpc calls
#### Protocol
+ gRPC/protobuf
+ GraphQL
+ compress binary
#### Transport
+ Tornado
+ WebSocket
+ HTTPS/REST

## How to use it


current status in development 0.0.1