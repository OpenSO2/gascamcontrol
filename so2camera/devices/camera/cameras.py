"""Implement pluggable interface for UV dual view cameras."""
import logging
from .camera import Camera

logger = logging.getLogger('myLog')


class Cameras():
    """Manage and sync dual view cameras."""
    def __init__(self):
        self._running = False
        self._issetup = False
        self.camera1 = None
        self.camera2 = None
        logger.info("__init__ cam done")

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

    async def init(self, loop):
        logger.info("init cam")
        self.camera1 = Camera("a")
        self.camera2 = None
        self.issetup = True

        await self.camera1.init(loop)
        logger.info("init cam done")

    async def start(self, loop):
        self.running = True
        img = await self.camera1.get(loop)
        return img

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
