"""Implement an interface for multi view cameras."""
import logging
import asyncio
import configargparse
from .camera import Camera


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Cameras():
    """Manage and sync multi view cameras."""

    def __init__(self):
        self.cameras = []
        self.logger = logging.getLogger('myLog')
        self.options = configargparse.options

        # figure out how many cameras we have to initialize
        self.cameras = [Camera(driver=driver, identifier=identifier)
                        for (driver, identifier)
                        in zip(self.options.camera_drivers,
                               self.options.camera_identifiers)]

    async def init(self):
        """Initialize all cameras."""
        camera_tasks = [cameras.init() for cameras in self.cameras]
        self.cameras = await asyncio.gather(*camera_tasks)
        self.logger.info("init cams done")

    async def get(self):
        """Get a full set of images by scheduling get from all concurrently."""
        camera_tasks = [cameras.get() for cameras in self.cameras]
        return await asyncio.gather(*camera_tasks)

    async def uninit(self):
        """Unitialize all cameras."""
        camera_tasks = [cameras.uninit() for cameras in self.cameras]
        self.cameras = await asyncio.gather(*camera_tasks)
        self.logger.info("uninit cams done")

    def __aenter__(self):
        await self.init()
        return self

    def __aexit__(self, *args):
        await self.uninit()
