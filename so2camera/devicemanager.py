"""Manage processes (not real proccesses, but async tasks)."""
#   - todo devicemanager: add spectro to queue
import asyncio
import logging
import configargparse
import conf
from processingqueue import CamQueueItem, Queue, ViscamQueueItem, SpecQueueItem
from devices.viscam.viscam import Viscam
from devices.camera.cameras import Cameras
from devices.camerashutter.camerashutter import Camerashutter
from spectrometry import Spectrometry


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    parser.add("--disableWebcam", default=False,
               help="Disable processing and saving of webcam images")
    parser.add("--disableSpectroscopy", default=False,
               help="Disable processing and saving of spectra")
    parser.add("--max_image_sets", default=-1,
               help="Only take N image sets and exit")
    parser.add("--darkframeintervall", default=100,
               help="Take N image sets between dark image sets")

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Devicemanager():
    """Manage Device tasks."""

    __monostate = None  # borg pattern

    def __init__(self):
        if Devicemanager.__monostate:
            self.__dict__ = Devicemanager.__monostate
        else:
            Devicemanager.__monostate = self.__dict__

            self.running = False
            self.task_names = ["cameras", "viscam", "spectroscopy"]
            self.loop = asyncio.get_event_loop()
            self.logging = logging.getLogger("myLog")
            self.running_tasks = []
            self.options = conf.Conf().options
            self.queue = Queue()
            self.noofimages = 0
            self.camerashutter = Camerashutter(
                driver=self.options.camerashutter_driver,
                device=self.options.camerashutter_device)
            self.options = conf.Conf().options

    async def viscam(self):
        """Run viscam and put images into queue."""
        async with Viscam() as viscam:
            while True:
                try:
                    img, meta = await viscam.get()
                    meta.type = "viscam"
                    await self.queue.push(ViscamQueueItem(img, meta))
                except asyncio.CancelledError:
                    self.logging.warning("Got CancelledError monitor_viscam")
                    break

    async def cameras(self):
        """Run cameras and put images into queue."""
        self.logging.debug("start cameras")
        async with Cameras() as cameras:
            self.logging.debug("cameras initialized")

            while True:
                try:
                    dark = not self.noofimages % self.options.darkframeinterval
                    if dark:
                        await self.camerashutter.close()
                        await self.cameras.set_exposure()
                    else:
                        await self.camerashutter.open()

                    self.logging.debug("get imageset")
                    images = await cameras.get()
                    for img, meta in images:
                        meta.dark = dark
                        meta.type = "camera"
                        await self.queue.push(CamQueueItem(img, meta))

                    self.noofimages += 1

                    # stop program if max images have been reached
                    # max_image_sets = -1 disables this check
                    max_image_sets = self.options.max_image_sets
                    if 0 < max_image_sets < self.noofimages:
                        self.options.stop = True

                except asyncio.CancelledError:
                    self.logging.warning("Got CancelledError cameras")
                    break

    async def spectroscopy(self):
        """Run spectroscopy and put spectra into queue."""

        async with Spectrometry as spectrometry:
            await spectrometry.calibrate()
            while True:
                try:
                    wavelengths, spectrum = spectrometry.measure()
                    meta = {
                        type: "spectrum"
                    }
                    await self.queue.push(SpecQueueItem(wavelengths,
                                                        spectrum, meta))
                except asyncio.CancelledError:
                    self.logging.warning("Got CancelledError spectroscopy")

    def start(self):
        """Set running flag to true and start tasks.

        This ONLY starts devices, not other systems.
        """
        task_names = self.task_names[:]
        self.logging.info("all devices: %s", task_names)
        if self.options.disableWebcam:
            task_names.remove("viscam")
        if self.options.disableSpectroscopy:
            task_names.remove("spectroscopy")

        task_names = list(set(task_names) - set(self.running_tasks))

        self.logging.info("start devices: %s", task_names)
        self.running_tasks = [self.loop.create_task(getattr(self, task_name)())
                              for task_name in task_names]
        self.running = True

    def stop(self):
        """Set running flag to false, tasks will stop themself.

        This ONLY stops devices, not other tasks.
        """
        for task in self.running_tasks:
            self.logging.info('cancel task %s', task)
            self.running_tasks.remove(task)
            task.cancel()
            self.logging.info('canceled')

        self.running = False
