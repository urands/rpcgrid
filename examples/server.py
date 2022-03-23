import rpcgrid as rpcg
import asyncio
from rpcgrid.providers import SocketProvider, LocalProvider


@rpcg.register
async def sum(x: int, y: int ) -> int:
    return x + y


async def main():
    rpcserver = await rpcg.server(SocketProvider(port=1234))
    rpcserver._loop.run_forever()

# Create RPC TCP server on port 1234

if __name__ == '__main__':
    print('Start server')
    asyncio.run(main())


