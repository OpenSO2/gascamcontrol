"""Command line spectrometry program for testing and demonstration."""
import asyncio
import logging
import csv
import configargparse
from spectrometry import Spectrometry
import conf


def save_spectrum(outfile, wavelengths, data):
    """Save spectrum to outfile."""
    with open(outfile, "wt") as csvfile:
        writer = csv.writer(csvfile)
        for dat in zip(wavelengths, data):
            writer.writerow(dat)


async def get_spectrum(driver, outfile):
    """Set single uncorrected spectrum."""
    async with Spectrometry(driver) as spectrometry:
        await spectrometry.calibrate()

        save_spectrum("dark-current.dat", spectrometry.wavelengths,
                      spectrometry.dark_current)
        save_spectrum("electronic_offset.dat", spectrometry.wavelengths,
                      spectrometry.electronic_offset)

        wavelengths, spectrum = await spectrometry.measure()

        noise = await spectrometry.calc_noise()
        exposure = spectrometry.calc_exposure(wavelengths, spectrum)
        exposure_opt = spectrometry.find_exposure_time(wavelengths,
                                                       spectrum)

        print("Exposure was {} ({}ms), optimal exposure time would be {} ms. "
              "Noise was {} ".format(exposure,
                                     spectrometry.exposure_ms,
                                     exposure_opt, noise))

        save_spectrum(outfile, spectrometry.wavelengths, spectrum)


def main():
    """Run main event loop."""
    parser = configargparse.get_argument_parser()
    parser.description = 'Spectrometry example program'
    parser.add_argument("--outfile", default="measurement.dat",
                        help="File to save spectrum to")
    parser.add_argument("--debug", action="store_true",
                        help="Print debug messaged")
    options = parser.parse_args()
    conf.Conf().options = options

    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_spectrum(options.spectrometer_driver,
                                         options.outfile))


if __name__ == "__main__":
    main()
