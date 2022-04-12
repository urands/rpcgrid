import asyncio
import logging
# from time import sleep
import time
import aiohttp

import rpcgrid
# from rpcgrid.base import Base
# from rpcgrid.providers import SocketProvider
from rpcgrid.providers.kafka import KafkaProvider
from rpcgrid.providers.kafkaconfluence import KafkaConfluenceProvider

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


async def worker(rpc):
    # First example
    print('First example')
    r = await rpc.read_root()
    print("RPC read_root:", r)

    # Second example
    print('Second example')
    cnt = 10
    tasks = []
    datas = '768676'*1
    for i in range(cnt):
        tsk = rpc.read_item(i, datas)
        tasks.append(tsk)
    start = time.time()
    results = await asyncio.gather(*tasks)
    print('RPC time:', time.time()-start)

    # print('Result:', results)
    #for t in tasks:
    #    print('Task profile:', t.time)
    # print('client:', tsk)
    # await asyncio.sleep(1000)


    # return
    urls = [f'http://127.0.0.1:5000/items/{i}?q={datas}' for i in range(cnt)]
    start = time.time()
    r = await async_aiohttp_get_all(urls)
    print('REST time:', time.time() - start)

    await rpc.close()
    # print(r)


async def async_aiohttp_get_all(urls):
    async def get_all(urls):
        async with aiohttp.ClientSession() as session:
            async def fetch(url):
                async with session.get(url) as response:
                    return await response.json()
            return await asyncio.gather(*[
                fetch(url) for url in urls
            ])
    # call get_all as a sync function to be used in a sync context
    return await get_all(urls)


async def main():
    # client_provider = KafkaConfluenceProvider('task_topic', bootstrap_servers='localhost:9091')
    client_provider = KafkaProvider('task_topic', bootstrap_servers='localhost:9091')
    rpcclient = await rpcgrid.client(client_provider)

    await worker(rpcclient)

if __name__ == '__main__':
    asyncio.run(main(), debug=True)
