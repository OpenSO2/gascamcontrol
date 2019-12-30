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
        self.cam = None
        self.drivername = driver
        self.identifier = identifier
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('myLog')

        # FIXME: path
        driver = ".".join(["devices", "camera",
                           "drivers", self.drivername, "camera"])
        self.driver = importlib.import_module(driver)
        self.camera = self.driver.camera()

        self.camera.identifier = self.identifier
        self.camera.dBufferlength = 1376256
        self.camera.dFixTime = 0
        self.camera.dExposureTime_a = 250000
        self.camera.dExposureTime_b = 250000

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate camera device."""
        self.logger.debug("init camera %s", self.identifier)
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.init, self.camera)
        self.logger.debug("init camera done.")

        self.logger.debug("camera set camera autoset exposure")
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.autosetExposure,
                                            self.camera)
        self.logger.debug("camera set autoset exposure done, camera ready")
        return self

    async def get(self):
        """Get a single image buffer."""
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.get, self.cam, 1)

        shape = (self.camera.height, self.camera.width, 1)
        return np.reshape(self.camera.buffer, shape).astype(np.uint16)

    async def stop(self):
        """Stop camera and release device."""
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.uninit, self.camera)
