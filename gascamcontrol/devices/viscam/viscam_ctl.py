"""Command line viscam program for testing and demonstration."""
import sys
import os
import logging
import asyncio
import cv2
import configargparse
import conf

PACKAGE_PARENT = '../..'
TOPLEVELPATH = os.path.realpath(os.path.join(os.getcwd(),
                                             os.path.expanduser(__file__)))
SCRIPT_DIR = os.path.dirname(TOPLEVELPATH)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from devices.viscam.viscam import Viscam  # noqa: E402,E501 pylint: disable=C0413,E0401


async def capture(filename):
    """Capture image from viscam and save to png or raw."""
    async with Viscam() as viscam:
        img = await viscam.get()
        cv2.imwrite(filename, img)


def main():
    """Run main event loop."""
    parser = configargparse.get_argument_parser()
    parser.description = 'Viscam example program'
    parser.add_argument("filename", default="out.png", help="file to save to")
    parser.add_argument("--debug", action="store_true",
                        help="Print debug messaged")
    options, _ = parser.parse_known_args()

    conf.Conf().options = options

    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(capture(options.filename))


if __name__ == "__main__":
    main()
