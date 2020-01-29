"""Command line viscam program for testing and demonstration."""
import sys
import os
import asyncio
import logging
from argparse import ArgumentParser
import cv2

PACKAGE_PARENT = '../..'
TOPLEVELPATH = os.path.realpath(os.path.join(os.getcwd(),
                                             os.path.expanduser(__file__)))
SCRIPT_DIR = os.path.dirname(TOPLEVELPATH)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from devices.viscam.viscam import Viscam


async def capture(driver, filename):
    """Capture image from viscam and save to png or raw."""
    async with Viscam(driver=driver) as viscam:
        img = await viscam.get()
        cv2.imwrite(filename, img)


def main():
    """Run main event loop."""
    parser = ArgumentParser(description='Viscam example program')
    parser.add_argument("filename", default="out.png", help="file to save to")
    parser.add_argument("--driver", default="mock",
                        help="Device driver to use (see ./drivers)")
    parser.add_argument("--debug", action="store_true",
                        help="Print debug messaged")
    options = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(capture(options.driver, options.filename))


if __name__ == "__main__":
    main()
