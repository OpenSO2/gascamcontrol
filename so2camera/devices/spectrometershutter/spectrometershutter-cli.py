"""Command line spectrometer shutter program for testing and demonstration."""
import sys
import os
import asyncio
from argparse import ArgumentParser

PACKAGE_PARENT = '../..'
TOPLEVELPATH = os.path.realpath(os.path.join(os.getcwd(),
                                             os.path.expanduser(__file__)))
SCRIPT_DIR = os.path.dirname(TOPLEVELPATH)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from devices.spectrometershutter.spectrometershutter import Spectrometershutter


async def set_shutter(driver, state, device, channel):
    """Set shutter to state."""
    async with Spectrometershutter(driver=driver, device=device, channel=channel) as specshut:
        await specshut.setState(state)


def main():
    """Run main event loop."""
    parser = ArgumentParser(description='Spectrometer shutter example program')
    parser.add_argument("state", default="open", help="[open|close] shutter")
    parser.add_argument("--driver", default="mock",
                        help="Device driver to use (see ./drivers)")
    options = parser.parse_args()
    loop = asyncio.get_event_loop()
    device = "/dev/ttyACM0"
    channel = 5
    loop.run_until_complete(set_shutter(options.driver, options.state, device,
                                        channel))


if __name__ == "__main__":
    main()
