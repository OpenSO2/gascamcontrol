"""Command line spectrometer program for testing and demonstration."""
import sys
import os
import logging
import asyncio
import csv
import configargparse
import conf

PACKAGE_PARENT = '../..'
TOPLEVELPATH = os.path.realpath(os.path.join(os.getcwd(),
                                             os.path.expanduser(__file__)))
SCRIPT_DIR = os.path.dirname(TOPLEVELPATH)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from devices.spectrometer.spectrometer import Spectrometer  # noqa: E402,E501 pylint: disable=C0413,E0401


async def get_spectrum(exposure, outfile):
    """Set single uncorrected spectrum."""
    async with Spectrometer() as spectrometer:
        wvl, spectrum = await spectrometer.get(exposure)

        if outfile:
            with open(outfile, 'w') as csvfile:
                writer = csv.writer(csvfile)
                for data in zip(wvl, spectrum):
                    writer.writerow(data)
        else:
            print('\n'.join([f"{s[0]} {s[1]}" for s in zip(wvl, spectrum)]))


def main():
    """Run main event loop."""
    parser = configargparse.get_argument_parser()
    parser.description = 'Spectrometer example program'
    parser.add_argument("--exposure", default=1E6, type=int,
                        help="Exposure time in us")
    parser.add_argument("--outfile", help="File to save spectrum to")
    parser.add_argument("--debug", action="store_true",
                        help="Print debug messaged")
    options = parser.parse_args()
    conf.Conf().options = options

    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_spectrum(options.exposure, options.outfile))


if __name__ == "__main__":
    main()
