"""Command line camera shutter program for testing and demonstration."""
import sys
import os
import asyncio
import logging
from argparse import ArgumentParser

PACKAGE_PARENT = '../..'
TOPLEVELPATH = os.path.realpath(os.path.join(os.getcwd(),
                                             os.path.expanduser(__file__)))
SCRIPT_DIR = os.path.dirname(TOPLEVELPATH)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from devices.camerashutter.camerashutter import Camerashutter  # noqa: E402,E501 pylint: disable=C0413,E0401


async def set_shutter(driver, state, device):
    """"""
    async with Camerashutter(driver=driver, device=device) as camshut:
        await camshut.setState(state)


def main():
    """Run main event loop."""
    parser = ArgumentParser(description='Camera shutter example program')
    parser.add_argument("state", default="open", help="[open|close] shutter")
    parser.add_argument("--driver", default="mock",
                        help="Device driver to use (see ./drivers)")
    parser.add_argument("--debug", action="store_true",
                        help="Print debug messaged")
    options = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)

    loop = asyncio.get_event_loop()
    device = ("/dev/serial/by-id/usb-Pololu_Corporation_"
              "Pololu_Micro_Maestro_6-Servo_Controller_00135615-if00")
    loop.run_until_complete(set_shutter(options.driver, options.state, device))


if __name__ == "__main__":
    main()
