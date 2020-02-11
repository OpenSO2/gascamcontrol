# pylint: disable=C0103
class BasePlugin():
    """Base class for plugins."""

    async def init(self):
        """Initiate plugin."""

    async def get_metadata(self):
        """Get a list of meta data entries to be saved alongside image sets."""
        return []

    async def uninit(self):
        """Tear down plugin."""

    async def __aenter__(self):
        return await self.init()

    async def __aexit__(self, *args):
        await self.uninit()
