"""Command line viscam program for testing and demonstration."""
import sys
import os
import asyncio
from argparse import ArgumentParser

import logging
logging.basicConfig(filename='example.log', level=logging.DEBUG)

PACKAGE_PARENT = '../..'
TOPLEVELPATH = os.path.realpath(os.path.join(os.getcwd(),
                                             os.path.expanduser(__file__)))
SCRIPT_DIR = os.path.dirname(TOPLEVELPATH)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from devices.camerashutter.camerashutter import Camerashutter


async def setShutter(driver, state, device):
    """"""
    async with Camerashutter(driver=driver, device=device) as camshut:
        await camshut.setState(state)


def main():
    """Run main event loop."""
    parser = ArgumentParser(description='Camera shutter example program')
    parser.add_argument("state", default="open", help="[open|close] shutter")
    parser.add_argument("--driver", default="mock",
                        help="Device driver to use (see ./drivers)")
    options = parser.parse_args()
    loop = asyncio.get_event_loop()
    device = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A402X19O-if00-port0"
    loop.run_until_complete(setShutter(options.driver, options.state, device))


if __name__ == "__main__":
    main()
