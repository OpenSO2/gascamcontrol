"""Implement pluggable interface for UV dual view cameras."""
import logging
import configargparse
from .camera import Camera


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    # fprintf(stderr, "   --noofimages n                Only save n UV image sets and exit\n");

    # Intervall (in images) between dark images
    # a dark image is taken every N images (int, >0)
    parser.add("--darkframeintervall", default=1000)


    # camera_drivers = "mock, mock, mock"
    # camera_identifiers = "a, b, c"

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Cameras():
    """Manage and sync dual view cameras."""

    def __init__(self):
        self._running = False
        self._issetup = False
        self.camera1 = None
        self.camera2 = None
        self.logger = logging.getLogger('myLog')
        self.logger.info("__init__ cam done")

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    @property
    def issetup(self):
        return self._issetup

    @issetup.setter
    def issetup(self, value):
        self._issetup = value

    async def init(self):
        self.logger.info("init cam")
        self.camera1 = Camera("mock", "a")
        self.camera2 = None
        self.issetup = True

        await self.camera1.start()
        self.logger.info("init cam done 2")

    async def start(self):
        self.running = True
        img = await self.camera1.get()
        return img

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
