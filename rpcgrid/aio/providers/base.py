class AsyncBaseProvider:

    # TODO: add suppor custom middlewares

    async def create(self):
        raise NotImplementedError("Providers must implement this method")

    async def open(self):
        raise NotImplementedError("Providers must implement this method")

    async def close(self):
        raise NotImplementedError("Providers must implement this method")

    def is_connected(self):
        raise NotImplementedError("Providers must implement this method")

    async def send(self, task):
        raise NotImplementedError("Providers must implement this method")

    async def recv(self):
        raise NotImplementedError("Providers must implement this method")

    async def call_method(self, task):
        if not self.is_connected():
            raise ConnectionError('Providers must be connected.')
        await self.send(task)
        task.status = task.status.PENDING
        return task
