import pytest

from rpcgrid.providers import LocalProvider

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_no_connection(event_loop):
    provider = LocalProvider()

    assert not provider.is_connected()
