"""Manage spectrometer."""
import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import configargparse
import conf


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()
    parser.add("--spectrometer_driver", default="mock",
               help="Which spectrometer driver to use")

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Spectrometer:
    """Define an interface for a spectrometer.

    Delegates the actual implementation to the drivers in ./drivers.
    """

    def __init__(self, driver=None):
        self.options = conf.Conf().options

        self.drivername = driver or self.options.spectrometer_driver
        self.loop = asyncio.get_event_loop()
        self.logging = logging.getLogger(__name__)

        driv = f"devices.spectrometer.drivers.{self.drivername}.spectrometer"
        self.driver = importlib.import_module(driv)
        self.spectrometer = self.driver.Spectrometer()

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate spectrometer device."""
        status = await self.loop.run_in_executor(
            ThreadPoolExecutor(), self.driver.init, self.spectrometer)

        self.logging.debug("spectrometer start")

        if status:
            raise Exception("Failed to start spectrometer")
        return self

    async def get(self, exposure):
        """Get a single spectrum."""
        self.spectrometer.integration_time_micros = int(exposure)
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.get, self.spectrometer)

        assert self.spectrometer.wavelengths, \
            "Spectrometer wavelenghts not set"

        return self.spectrometer.wavelengths, self.spectrometer.lastSpectrum

    async def stop(self):
        """Stop viscam and release device."""
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.uninit, self.spectrometer)
