"""Manage spectrometer shutter.
"""
import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from log import stdout_redirector


class Spectrometershutter():
    """
    Delegates the actual implementation to the drivers in ./drivers.
    """

    def __init__(self, driver, device, channel):
        self.drivername = driver
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('myLog')

        driver = f"devices.spectrometershutter.drivers.{self.drivername}.spectrometershutter"
        self.driver = importlib.import_module(driver)
        self.spectrometershutter = self.driver.camerashutter()
        self.spectrometershutter.device = device
        self.spectrometershutter.channel = channel

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate spectrometer shutter device."""
        print("start")
        print("inited", self.spectrometershutter,  self.spectrometershutter.device)
        # with stdout_redirector():
        st = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                             self.driver.init, self.spectrometershutter)
        print("inited", self.spectrometershutter,  self.spectrometershutter.device)
        if st:
            print("ERRROROROR!")
            print(f"fff {st}")
            # FIXME
            # raise
        return self

    async def setState(self, state):
        """ """
        print("set")
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.setState,
                                            self.spectrometershutter, state)

    async def stop(self):
        """Stop spectrometer shutter and release device."""
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.uninit, self.spectrometershutter)
