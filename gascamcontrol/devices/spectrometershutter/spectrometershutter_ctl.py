"""Command line spectrometer shutter program for testing and demonstration."""
import asyncio
import logging
from argparse import ArgumentParser
from .spectrometershutter import Spectrometershutter


async def set_shutter(state):
    """Set shutter to state."""
    async with Spectrometershutter() as specshut:
        await specshut.set_state(state)


def main():
    """Run main event loop."""
    parser = ArgumentParser(description='Spectrometer shutter example program')
    parser.add_argument("state", default="open", help="[open|close] shutter")
    parser.add_argument("--debug", action="store_true",
                        help="Print debug messaged")
    options = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_shutter(options.state))


if __name__ == "__main__":
    main()
