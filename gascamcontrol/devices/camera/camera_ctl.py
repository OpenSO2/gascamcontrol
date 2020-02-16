"""Example cli program to drive the cameras, intended for testing only."""
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

from devices.camera.camera import Camera  # noqa: E402,E501 pylint: disable=C0413,E0401


async def capture(driver, filename, identifier):
    """Capture image from viscam and save to png or raw."""
    async with Camera(driver=driver, identifier=identifier) as camera:
        print("cli inited, get image")
        img, _meta = await camera.get()
        print("cli got image")
        if ".png" in filename:
            # upsample image to use full 16bit range (the image will be very
            # dark otherwise)
            img *= 16

            cv2.imwrite(filename, img)
        else:
            with open(filename, 'wb') as file:
                img.tofile(file)


def main():
    """Run main event loop."""
    parser = ArgumentParser(description='Viscam example program')
    parser.add_argument('camid', help='camera identifier, <a|b>')
    parser.add_argument("filename", default="out.png", help="file to save to")
    parser.add_argument("--driver", default="mock",
                        help="Device driver to use (see ./drivers)")
    parser.add_argument("--debug", action="store_true",
                        help="Print debug messaged")
    options = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(capture(options.driver, options.filename,
                                    options.camid))


if __name__ == "__main__":
    main()