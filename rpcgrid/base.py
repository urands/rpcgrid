import asyncio
import signal
from logging import getLogger

log = getLogger(__name__)


class Base:
    def __init__(self, provider, loop=None):
        self._provider = provider
        self._running = True
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

    def __del__(self):
        self.close()

    @property
    def running(self):
        return self._running

    @property
    def provider(self):
        return self._provider

    def close(self, *args):
        self._running = False
        self._provider.close()
        print('provider close ok')

    def run(self):
        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)
        self._loop.run_forever()
