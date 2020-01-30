class BasePlugin():
    """Base class for plugins."""

    async def init(self):
        pass

    async def get_metadata(self):
        """Get a list of meta data entries to be saved alongside image sets."""
        return []

    async def uninit(self):
        pass

    async def __aenter__(self):
        return await self.init()

    async def __aexit__(self, *args):
        await self.uninit()
