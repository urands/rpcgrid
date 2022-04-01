import asyncio
import signal
from logging import getLogger

log = getLogger(__name__)


class Base:
    def __init__(self, provider, loop=None):
        self._provider = provider
        self._running = True
        #if loop is None:
        #    loop = asyncio.get_event_loop()
        self._loop = loop

    def __del__(self):
        pass
        # self._loop.run_until_complete(self.close())

    @property
    def running(self):
        return self._running

    @property
    def provider(self):
        return self._provider

    async def close(self, *args):
        self._running = False
        await self._provider.close()
        log.info('provider close ok')

    async def run(self):
        # signal.signal(signal.SIGINT, self.close)
        # signal.signal(signal.SIGTERM, self.close)
        # self._loop.run_forever()
        pass
