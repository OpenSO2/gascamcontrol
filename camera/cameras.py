"""Implement pluggable interface for UV dual view cameras."""

from concurrent.futures import ThreadPoolExecutor
import logging
from .camera_py import (camera_init, sSO2Parameters, config,
                       camera_autosetExposure, camera_get, camera_uninit)
from log import OutputGrabber


logger = logging.getLogger('myLog')


class Camera():
    """Manage a camera device through a driver. Abstract c nastyness."""

    def __init__(self, id):
        self.isready = False
        self.cam = None
        self.identifier = id
        logger.info("__init__ cam done")

    async def init(self, loop):
        logger.info("init cams")
        cam = sSO2Parameters()
        cam.identifier = self.identifier
        self.cam = cam
        conf = config()
        conf.dBufferlength = 1376256
        conf.dFixTime = 0
        conf.dExposureTime_a = 250000
        conf.dExposureTime_b = 250000

        logger.info("init camera...")
        await loop.run_in_executor(ThreadPoolExecutor(), camera_init, cam)
        logger.info("init camera done.")

        logger.info("camera set camera autoset exposure")
        # stat = camera_autosetExposure(cam, conf)
        stat = await loop.run_in_executor(ThreadPoolExecutor(),
                                          camera_autosetExposure, cam, conf)
        if stat:
            print("failed to find exposure")
            return -1
        logger.info("camera set camera autoset exposure done, init camera")

        self.isready = True
        logger.info("init cams done")
        return cam

    async def get(self, loop):
        logger.info("camera get image")

        out = OutputGrabber(threaded=True)
        with out:
            stat = await loop.run_in_executor(ThreadPoolExecutor(), camera_get,
                                              self.cam, 1)
        if stat:
            logger.error("failed to get image from camera")
        # return -1
        import numpy as np
        width, height = 1344, 1024

        arr = []
        for i in range(width * height):
            arr.append(self.cam.getBuffer(i))

        arrarr = np.array(arr)
        logger.warning("arr content:")
        img = np.reshape(arrarr, (height, width, 1)).astype(np.uint16)
        # logger.warning(f"arr length: {len(arr)} {width*height} {img.shape} {arrarr[100:200]}")
        return img
        # # create new image to hold the loaded data
        # img = np.zeros((width, height, 1), np.uint16)
        #
        # arr = []
        # for i in range(width * height):
        #     arr.append(self.cam.getBuffer(i))
        #
        # arrarr = np.array(arr)
        # img = np.reshape(arrarr, (height, width, 1)).astype(np.uint16)
        #
        # yield img
        # return img
    # def __enter__(self):
    #     camera_init()
    #
    # def __exit__(self, *args):
    #     camera_uninit()


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
        # print(img)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
