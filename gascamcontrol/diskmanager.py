"""Handle I/O interactions."""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
import configargparse
import cv2
import conf


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    parser.add("--FileNamePrefix", default="testing",
               help="Prefix for all images in this session")

    # path to images and logs - can be either a relative path from the
    # working directory or an absolute path
    # eg.
    #     ./measurement-stromboli-2016
    #     /home/so2/measurements
    #
    # Trailing "/" will be stripped.
    # Files will be saved in a subfolder of the form
    # `ImagePath`/YYYY-MM-DD_HH_MM/
    # Log files will be saved in a subfolder of the form `ImagePath/logs`
    # fixme: create subfolder
    # fixme: save logs
    parser.add("--imagePath", default="images",
               help="Path to images and logs - can be either a relative path "
                    "from the working directory or an absolute path")
    # fprintf(stderr, "   --png-only             Skip saving of raw files\n");

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Diskmanager():
    """Handle Tasks related to writing to disk, incl file formats and such."""

    __monostate = None  # borg pattern

    def __init__(self):
        if Diskmanager.__monostate:
            self.__dict__ = Diskmanager.__monostate
        else:
            Diskmanager.__monostate = self.__dict__

            self.loop = asyncio.get_event_loop()
            self.logging = logging.getLogger(__name__)
            self.options = conf.Conf().options
            self.noofimages = 0
            self.noofviscam = 0

    async def save(self, item):
        """Save an arbitrary item, decide handling from meta data."""
        await getattr(self, "save_"+item.meta["type"])(item)

    async def save_camera(self, item):
        """Sava a camera image."""
        assert "date" in item.meta, "no date found in camera meta data"
        filename = f"{self.options.imagePath}/{str(item.meta['date'])}.png"
        self.logging.info("saving image to path %s", filename)
        img = item.data * 16  # fixme: should depend on depth
        # TODO save meta data

        write_status = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                                       cv2.imwrite,
                                                       filename, img)

        if write_status:
            self.logging.info("image written (%s)", self.noofimages)
        else:
            self.logging.error("couldn't write image to %s", filename)
            # TODO: raise some sort of exception?

        self.noofimages += 1

    async def save_viscam(self, item):
        """Save a viscam image."""
        assert "date" in item.meta, "no date found in viscam meta data"

        date = str(item.meta['date'])
        filename = f"{self.options.imagePath}/viscam-{date}.jpg"
        self.logging.debug("saving viscam image to path %s", filename)

        write_status = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                                       cv2.imwrite,
                                                       filename, item.data)
        if write_status:
            self.logging.debug("viscam image written (%s)", self.noofimages)
        else:
            self.logging.error("couldn't write viscam image to %s", filename)
            # TODO: raise some sort of exception?

        self.noofviscam += 1
