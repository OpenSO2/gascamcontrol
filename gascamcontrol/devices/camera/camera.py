"""Implement pluggable interface for UV dual view cameras."""
import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import datetime
import logging
import numpy as np
# import configargparse


def _setup():
    """Do setup that needs to happen once on import."""
    # parser = configargparse.get_argument_parser()

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Camera():
    """Manage a camera device through a driver."""

    def __init__(self, driver, identifier):
        self.drivername = driver
        self.identifier = identifier
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger(__name__)
        self.logging = self.logger
        self.logging.info("init camera %s %s", driver, identifier)

        driver = f".drivers.{self.drivername}.camera"
        self.driver = importlib.import_module(driver, package=__package__)
        self.camera = self.driver.camera()

        self.logger.debug("identifier %s", self.identifier)
        self.camera.identifier = self.identifier
        self.camera.exposuretime = 250000  # start exposure time

    # def __str__(self):
    #     return f"Camera {self.drivername} {self.identifier}"

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate camera device."""
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.init, self.camera)

        return self

    async def set_exposure(self):
        """Trigger a exposure correction in driver."""
        self.logger.debug("camera set autoset exposure")
        return await self.loop.run_in_executor(ThreadPoolExecutor(),
                                               self.driver.autosetExposure,
                                               self.camera)

    async def get(self):
        """Get a single image buffer."""
        self.logger.info("get buffer %s", self.camera.identifier)

        stat = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                               self.driver.get,
                                               self.camera, 1)

        self.logger.debug("set.driver.get %s", stat)
        self.logger.debug("got... %s %i %i %i", self.camera.identifier,
                          self.camera.stBufferSize,
                          self.camera.height, self.camera.width)

        shape = (self.camera.height, self.camera.width, 1)
        img = np.reshape(np.array(self.camera.buffer), shape).astype(np.uint16)
        meta = {
            "id": self.identifier,
            "date": datetime.datetime.now(),
            "height": self.camera.height,
            "width": self.camera.width,
            "depth": self.camera.depth
        }
        return img, meta

    async def stop(self):
        """Stop camera and release device."""
        self.logger.debug("stop camera")
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.uninit, self.camera)
        self.logger.debug("stoped camera")
