"""Implement pluggable interface for UV dual view cameras."""
import logging
from .camera import Camera


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
