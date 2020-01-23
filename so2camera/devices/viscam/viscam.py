"""Manage viscam.

Viscam are auxilary visual cameras (think cheap webcams) that are
not part of the main measurement.
"""
import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import numpy as np
import configargparse
import conf


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()
    parser.add("--viscam_driver", default="mock",
               help="which viscam driver to use")
    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Viscam():
    """Define an interface for a visual camera (eg. webcam).

    Delegates the actual implementation to the drivers in ./drivers.
    """

    def __init__(self, driver=None):
        self.options = conf.Conf().options
        self.drivername = driver or self.options.viscam_driver
        self.loop = asyncio.get_event_loop()
        self.logging = logging.getLogger('myLog')
        visdriv = f"devices.viscam.drivers.{self.drivername}.viscam"
        self.driver = importlib.import_module(visdriv)
        self.viscam = self.driver.viscam()

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate viscam device."""

        state = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                                self.driver.init, self.viscam)
        if state:
            self.logging.error("error init viscam")
        return self

    async def get(self):
        """Get a single image buffer."""
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.get, self.viscam)

        shape = (self.viscam.height, self.viscam.width, 3)
        return np.reshape(self.viscam.buffer, shape)

    async def stop(self):
        """Stop viscam and release device."""
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.uninit, self.viscam)
