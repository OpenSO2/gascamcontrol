"""Capture GPS location.

A simple GPS plugin that gets the current position from gpsd and injects
that into the image set meta data.
"""
import logging
import asyncio
from plugins.gps import aiogps
from plugins.basePlugin import BasePlugin


class Plugin(BasePlugin):
    """Plugin to read gpsd device.

    >>> async def _test():
    ...    async with Plugin() as plugin:
    ...        return await plugin.get_metadata()
    >>> import asyncio
    >>> md = asyncio.new_event_loop().run_until_complete(_test())
    >>> "latitude" in md
    True
    >>> "longitude" in md
    True
    >>> "altitude" in md
    True
    """

    def __init__(self):
        super().__init__()
        self.position = {
            "latitude": None,
            "longitude": None,
            "altitude": None
        }
        self.gps_watch = None
        self.logging = logging.getLogger(__name__)
        self.loop = asyncio.get_event_loop()

    async def init(self):
        """Start background task to watch for gpsd updates."""
        self.gps_watch = self.loop.create_task(self._start_gps_watch())
        return self

    async def _start_gps_watch(self):
        """Run continuously to get a position fix and save to self.position."""
        try:
            async with aiogps.aiogps() as gpsd:
                async for _ in gpsd:
                    if gpsd.fix.status:
                        self.position = vars(gpsd.fix)

        except asyncio.CancelledError:
            return
        except asyncio.IncompleteReadError:
            self.logging.info('Connection closed by server')
        except asyncio.TimeoutError:
            self.logging.error('Timeout waiting for gpsd to respond')

    async def get_metadata(self):
        """Get geolocation via gpsd.

        Because GPSes can take a significant time to get a position fix, this
        will return the last know position even if its none.
        """
        return self.position

    async def uninit(self):
        """Stop background task watching gpsd."""
        self.gps_watch.cancel()


async def _test():
    logging.basicConfig(level=logging.DEBUG)
    async with Plugin() as plugin:
        position = await plugin.get_metadata()

        while not position.longitude:
            await asyncio.sleep(.2)
            position = plugin.get_metadata()

        print(position)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(_test())
