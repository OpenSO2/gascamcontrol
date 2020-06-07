"""Manages spectrometry and wrapp spectrometer.py.

Ported from spectrometry.c
"""
import logging
import configargparse
import numpy as np
from devices.spectrometer.spectrometer import Spectrometer
import conf


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    # The DOAS method depends on a good exposure in the region of SO2
    # absorption (region of interest, roi). An appropriate saturation is
    # at about 70% of the maximum value of the spectrometer (typically
    # 16bit, 65535). This is calculated from the highest value in the
    # roi at a given exposure time.
    # The upper and lower bounds of the roi are important, because SO2
    # absorption drops over ~310nm, but sunlight dramatically diminishes
    # with wavelengths <340. If the upper limit is set too low, not enough
    # sunlight is present. If it is too high, SO2 absorption is negligible.
    parser.add("--spectrometry_roi_lower", default=300,
               help="Lower bound on wavelength region of interest in nm")
    parser.add("--spectrometry_roi_upper", default=320,
               help="Upper bound on wavelength region of interest in nm")

    parser.add("--spectrometer_calibrate_intervall", default=10,
               help="recalibrate every N scans")

    parser.add("--dark_current_integration_time_s", default=60)

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Spectrometry:
    """Handle basic spectrometric functionality."""

    def __init__(self):
        self.logging = logging.getLogger(__name__)
        self.options = conf.Conf().options
        self.spectrometer = Spectrometer()
        # driver=self.options.spectrometer_driver)
        self.electronic_offset = None
        self.dark_current = None
        self.no_of_scans = 1
        self.wavelengths = None
        self.max = 0
        self.spectrum_length = 0

        # set 1s as initial integration time
        self.exposure_us = 1000 * 1000

    async def __aenter__(self):
        return await self.init()

    async def __aexit__(self, *args):
        await self.uninit()

    async def init(self):
        """Initialize spectrometry and spectrometer."""
        await self.spectrometer.start()
        self.max = self.spectrometer.spectrometer.max
        self.spectrum_length = self.spectrometer.spectrometer.spectrum_length
        return self

    def calc_exposure(self, wavelengths, spectrum):
        """Calculate absolute exposure in the region of interest.

        For SO2 measurements, the roi is between 300 and 325nm.
        """
        roi_l, roi_u = (self.options.spectrometry_roi_lower,
                        self.options.spectrometry_roi_upper)

        roi = [i for i in zip(wavelengths, spectrum) if roi_l <= i[0] <= roi_u]

        _, roi_spectrum = zip(*roi)
        return max(roi_spectrum)  # should be something between 0..max

    def find_exposure_time(self, wavelengths, spectrum):
        """Calculate the optimal exposure time in the relevant spectral region.

        The saturation T of a detector pixel P is defined as:
               C(P)
        T(P) = ----------
             N · Cmax
        C = counts in pixel
        N = number of scans = 1
        C_max = 4096 for the USB2000+
            above 80% the sensitivity drops of, so a good saturation is at
            about .7, thus:
        T_opt = C_opt/Cmax = .7
            if t is the exposure time, since T ~ t
            T_opt     t_opt
        -----  =  -----
        T_arb     t_arb
            Thus:
               .7 · t_arb
        t_opt =   ----------   = .7 · t_arb · Cmax / C_arb
                  T_arb
        """
        exposure = self.calc_exposure(wavelengths, spectrum)
        self.logging.debug(
            "spectro: find exposure time inttime: %s, max: %s, exposure: %s",
            self.exposure_us, self.max, exposure)

        assert self.exposure_us, "exposure_us not set, maybe calibrate first?"
        assert self.max, "exposure_us not set, maybe init first?"
        return .7 * self.exposure_us * self.max / exposure

    async def calibrate(self):
        """Calc and set electronic offset and dark current for corrections.

        FIXME: Shutter needs to be closed for this.
        FIXME: set integration time and no_of_scans
        """
        self.logging.info("spectrometry: Measuring electronic offset")
        self.electronic_offset = await self.mean(10000, 3000)

        self.logging.info("spectrometry: Measuring dark current")
        dcit = self.options.dark_current_integration_time_s
        self.dark_current = await self.mean(1, dcit * 1E6)

    async def calc_noise(self):
        """Calculate photon noise."""
        # take two measurements in quick succession
        spectrum1 = await self.mean_and_substract(1, 1 * 1000 * 1000)
        spectrum2 = await self.mean_and_substract(1, 1 * 1000 * 1000)

        # calc std deviation and average difference
        diff = abs(np.array(spectrum1) - np.array(spectrum2)).sum()

        # sigma_I = sigma_D / √2
        photon_noise = diff / np.sqrt(2)
        self.logging.debug("spectrometry: photon noise is %s", photon_noise)

        return photon_noise

    async def mean_and_substract(self, number_of_spectra, exposure_us):
        """Average N corrected (!) spectra of M exposure."""
        spectrum = np.zeros(self.spectrum_length)

        dcit = self.options.dark_current_integration_time_s * 1E6
        scale = exposure_us / dcit

        for _ in range(number_of_spectra):
            _, dat = await self.spectrometer.get(exposure_us)
            spectrum += np.array(dat)
            spectrum -= np.array(self.electronic_offset)
            # substract dark current, scaled by integration time
            spectrum -= np.array(self.dark_current) * scale

        # fixme RuntimeWarning: invalid value encountered in true_divide
        return spectrum / number_of_spectra

    async def mean(self, number_of_spectra, exposure_ms):
        """Average N uncorrected (!) spectra of M exposure."""
        spectrum = np.zeros(self.spectrum_length)

        for _ in range(number_of_spectra):
            wavelengths, dat = await self.spectrometer.get(exposure_ms)
            spectrum += np.array(dat)

        self.wavelengths = wavelengths
        return spectrum / number_of_spectra

    async def measure(self):
        """Take a measurement."""
        self.logging.debug("spectrometry: start measurement %i, %i",
                           self.no_of_scans, self.exposure_us)
        spectrum = await self.mean_and_substract(self.no_of_scans,
                                                 self.exposure_us)
        self.logging.info("spectrometry: measurement done")
        return self.wavelengths, spectrum

    async def uninit(self):
        """Uninit spectrometry and spectrometer."""
        return await self.spectrometer.stop()
