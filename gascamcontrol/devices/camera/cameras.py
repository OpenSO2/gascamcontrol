"""Implement an interface for multi view cameras."""
import logging
import asyncio
import configargparse
import conf
from devices.camera.camera import Camera


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    # FIXME
    # parser.add("--InterFrameDelay", default=10,
    #            help="delay between two frames in ms")
    # parser.add("--FixTime", default=0,
    #            help="fix exposure time 1 = yes 0 = no")

    # contains the Exposuretime in [us]
    # min = 2.4 max = 1004400
    # parser.add("--ExposureTime_a", default=1004400)
    # parser.add("--ExposureTime_b", default=1004400)

    parser.add("--camera_drivers", nargs="*")
    parser.add("--camera_identifiers", nargs="*")

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Cameras():
    """Manage and sync multi view cameras."""

    def __init__(self):
        self.cameras = []
        self.logger = logging.getLogger('myLog')
        self.logging = self.logger
        self.logger.info("initialize cameras")

        self.options = conf.Conf().options

        self.logger.info("cameras to init: %s, %s ",
                         self.options.camera_drivers,
                         self.options.camera_identifiers)

        # figure out how many cameras we have to initialize
        # Camera(driver="phx", identifier="a")
        self.cameras = [Camera(driver=driver, identifier=identifier)
                        for (driver, identifier)
                        in zip(self.options.camera_drivers,
                               self.options.camera_identifiers)]

        self.logging.info("cameras init: %s", self.cameras)

    async def init(self):
        """Initialize all cameras."""
        self.logger.debug("collect all cameras to start")
        camera_tasks = [cameras.start() for cameras in self.cameras]
        self.logger.debug("start all cameras %s", camera_tasks)
        self.cameras = await asyncio.gather(*camera_tasks)
        self.logger.debug("all cameras started")

    async def get(self):
        """Get a full set of images by scheduling get from all concurrently."""
        camera_tasks = [cameras.get() for cameras in self.cameras]
        return await asyncio.gather(*camera_tasks)

    async def set_exposure(self):
        """Trigger all cameras to set a new exposure value."""
        camera_tasks = [cameras.set_exposure() for cameras in self.cameras]
        return await asyncio.gather(*camera_tasks)

    async def uninit(self):
        """Unitialize all cameras."""
        camera_tasks = [cameras.stop() for cameras in self.cameras]
        self.cameras = await asyncio.gather(*camera_tasks)
        self.logger.info("uninit cams done")

    async def __aenter__(self):
        self.logger.info("cameras aenter")
        await self.init()
        return self

    async def __aexit__(self, *args):
        await self.uninit()
