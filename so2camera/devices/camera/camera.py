"""Implement pluggable interface for UV dual view cameras."""
import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import numpy as np
from log import stdout_redirector


class Camera():
    """Manage a camera device through a driver."""

    def __init__(self, driver, identifier):
        self.drivername = driver
        self.identifier = identifier
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('myLog')

        driver = f"devices.camera.drivers.{self.drivername}.camera"
        self.driver = importlib.import_module(driver)
        self.camera = self.driver.camera()

        print(f"identifier '{self.identifier}'")
        self.camera.identifier = self.identifier
        self.camera.exposuretime = 250000  # start exposure time

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate camera device."""
        self.logger.debug("init camera %s", self.identifier)
        with stdout_redirector():
            print("stdout_redirector done")
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.init, self.camera)
        self.logger.debug("init camera done.")

        self.logger.debug("camera set camera autoset exposure")
        print("camera set camera autoset exposure")
        # FIXME: Im not sure this should be here... maybe own method?
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.autosetExposure,
                                            self.camera)
        self.logger.debug("camera set autoset exposure done, camera ready")
        print("camera set autoset exposure done, camera ready")
        return self

    async def get(self):
        """Get a single image buffer."""
        # with stdout_redirector():
        print("async def get")
        stat = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                               self.driver.get,
                                               self.camera, 1)
        print(f"set.driver.get {stat}")
        print("got...", self.camera.identifier, self.camera.stBufferSize,
              self.camera.height, self.camera.width)

        shape = (self.camera.height, self.camera.width, 1)
        return np.reshape(np.array(self.camera.buffer), shape).astype(np.uint16)

    async def stop(self):
        """Stop camera and release device."""
        print("stop")
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.uninit, self.camera)
        print("stoped")
