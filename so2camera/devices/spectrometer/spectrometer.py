"""Manage viscam.

Viscam are auxilary visual cameras (think cheap webcams) that are
not part of the main measurement.
"""
import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from log import stdout_redirector


class Spectrometer():
    """Define an interface for a spectrometer.

    Delegates the actual implementation to the drivers in ./drivers.
    """

    def __init__(self, driver):
        self.drivername = driver
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('myLog')

        visdriv = f"devices.spectrometer.drivers.{self.drivername}.spectrometer"
        self.driver = importlib.import_module(visdriv)
        self.spectrometer = self.driver.spectrometer()

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate spectrometer device."""
        print("start")
        # with stdout_redirector():
        print("slljfdg")
        st = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                             self.driver.init, self.spectrometer)

        if st:
            print("ERRROROROR!")
            print(f"fff {st}")
        return self

    async def get(self, exposure, scans):
        """Get a single spectrum."""
        print("get", exposure, scans)
        self.spectrometer.integration_time_micros = exposure
        self.spectrometer.scans = scans
        # with stdout_redirector():
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.get, self.spectrometer)

        return self.spectrometer.wavelengths, self.spectrometer.lastSpectrum

    async def stop(self):
        """Stop viscam and release device."""
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.uninit, self.spectrometer)
