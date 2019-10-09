# RPCGrid (development)

Remote procedure call package for any protocol and any transport layer.

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

#### Server side
```python
import rpcgrid
from rpcgrid.providers import SocketProvider

@rpcgrid.register
def sum(x, y): 
    return x + y

# Create RPC TCP server on port 1234
rpcserver = rpcgrid.create(SocketProvider(port = 1234))
rpcserver.run()
```


#### Client side

```python
import rpcgrid
from rpcgrid.providers import SocketProvider

# Open connection with server  
rpc = rpcgrid.open(SocketProvider('localhost:1234'))

# Call RPC sum  and wair results 
print( rpc.sum(1,2).wait() )
```

current status in development 0.0.1