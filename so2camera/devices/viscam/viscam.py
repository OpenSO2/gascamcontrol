"""Manage viscam.

Viscam are auxilary visual cameras (think cheap webcams) that are
not part of the main measurement.
"""
import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import numpy as np
from log import stdout_redirector


class Viscam():
    """Define an interface for a visual camera (eg. webcam).

    Delegates the actual implementation to the drivers in ./drivers.
    """

    def __init__(self, driver):
        self.drivername = driver
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('myLog')

        # FIXME: path
        print(f"__file__={__file__}")
        print(f"__name__={__name__}")
        print(f"__package__={str(__package__)}")

        visdriv = f"devices.viscam.drivers.{self.drivername}.viscam"
        self.driver = importlib.import_module(visdriv)
        self.viscam = self.driver.viscam()

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate viscam device."""
        print("start")
        with stdout_redirector():
            print("slljfdg")
            st = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                                 self.driver.init, self.viscam)

        if st:
            print("ERRROROROR!")
            print(f"fff {st}")
        return self

    async def get(self):
        print("get")
        """Get a single image buffer."""
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.get, self.viscam)

        shape = (self.viscam.height, self.viscam.width, 3)
        return np.reshape(self.viscam.buffer, shape)

    async def stop(self):
        """Stop viscam and release device."""
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.uninit, self.viscam)
