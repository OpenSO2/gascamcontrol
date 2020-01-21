"""Command line spectrometer program for testing and demonstration."""
import sys
import os
import asyncio
import csv
from argparse import ArgumentParser

PACKAGE_PARENT = '../..'
TOPLEVELPATH = os.path.realpath(os.path.join(os.getcwd(),
                                             os.path.expanduser(__file__)))
SCRIPT_DIR = os.path.dirname(TOPLEVELPATH)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from devices.spectrometer.spectrometer import Spectrometer


async def get_spectrum(driver, exposure, scans, outfile):
    """Set shutter to state."""
    async with Spectrometer(driver=driver) as spectrometer:
        spectrum = await spectrometer.get(exposure, scans)

        if outfile:
            with open(outfile, 'w') as csvfile:
                writer = csv.writer(csvfile)
                for data in spectrum:
                    writer.writerow(data)
        else:
            print('\n'.join([f"{s[0]} {s[1]}" for s in spectrum]))


def main():
    """Run main event loop."""
    parser = ArgumentParser(description='Spectrometer shutter example program')
    parser.add_argument("exposure", default=1E6, type=int, help="Exposure time in ms")
    parser.add_argument("scans", default=1, type=int, help="Number of scans")
    parser.add_argument("--outfile", help="File to save spectrum to")
    parser.add_argument("--driver", default="mock",
                        help="Device driver to use (see ./drivers)")
    options = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_spectrum(options.driver, options.exposure, options.scans,
                                         options.outfile))


if __name__ == "__main__":
    main()
