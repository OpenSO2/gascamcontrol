"""Capture GPS location.

A simple GPS plugin that gets the current position from gpsd and injects
that into the image set meta data.
"""
import logging
import asyncio
from gps import aiogps
from basePlugin import BasePlugin


class Plugin(BasePlugin):
    """Plugin to read gpsd device.

    >>> async with Plugin() as plugin:
            md = await plugin.get_metadata()
    >>> bool(md.latitude)
    True
    >>> assert(md.longitude)
    True
    >>> assert(md.altitude)
    True
    """

    def __init__(self):
        super().__init__()
        self.position = None
        self.gps_watch = None
        self.logging = logging.getLogger("myLog")
        self.loop = asyncio.get_event_loop()

    async def init(self):
        self.gps_watch = self.loop.create_task(self._start_gps_watch())
        return self

    async def _start_gps_watch(self):
        """Run continuesly to get a position fix and save to self.postion."""
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
        will return the last know position and sleeps until it gets one.
        """
        while not self.position:
            await asyncio.sleep(.2)

        return self.position

    async def uninit(self):
        self.gps_watch.cancel()


async def _test():
    logging.basicConfig(level=logging.DEBUG)
    async with Plugin() as plugin:
        print(await plugin.get_metadata())

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(_test())
