class BaseProtocol:

    async def encode(self, task):
        raise NotImplementedError("Providers must implement this method")

    async def decode(self, data):
        raise NotImplementedError("Providers must implement this method")