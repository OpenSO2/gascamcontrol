"""Handle I/O interactions."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import cv2
import configargparse
import log
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
    # fprintf(stderr, "   --png-only                    Skip saving of raw files\n");

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Io():
    """Handle Tasks related to writing to disk, incl file formats and such."""

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.logging = log.Log('myLog')
        self.options = conf.Conf().options


    async def save_png(self, filename, img):
        """Save a png file to disk."""
        img *= 16
        await self.loop.run_in_executor(ThreadPoolExecutor(), cv2.imwrite,
                                        filename, img)

    async def save(self, item):
        """Save an arbitrary item, decide handling from meta data."""
        filename = f"{self.options['imagePath']}/{str(item.meta['date'])}.png"
        self.logging.info("saving image to path %s", filename)
        img = item.data * 16  # fixme: should depend on depth
        # TODO save meta data

        # await asyncio.sleep(4)

        write_status = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                                       cv2.imwrite,
                                                       filename, img)

        if write_status:
            self.logging.info("image written")
        else:
            self.logging.error("couldn't write image")
