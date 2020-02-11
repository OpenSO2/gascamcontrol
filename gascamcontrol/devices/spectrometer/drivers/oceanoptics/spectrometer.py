from seabreeze import spectrometers


def init(spectro):
    """Find and init spectrometer."""
    spectro.spectrometer = spectrometers.Spectrometer.from_first_available()

    spectro.wavelengths = spectro.spectrometer.wavelengths()
    spectro.spectrum_length = len(spectro.wavelengths)
    spectro.max = 65535


def get(spectro):
    """Get a spectrum."""
    spectro.spectrometer.integration_time_micros(
        spectro.integration_time_micros)
    spectro.lastSpectrum = spectro.spectrometer.intensities()


def uninit(spectro):
    """Tear down."""
    spectro.spectrometer = None


class Spectrometer():  # pylint: disable=too-few-public-methods
    """Provide support for an oceanoptics spectrometer.

    Pretty much just a wrapper for seabreeze, to keep consistent with other
    devices.
    """

    spectrometer = None
    lastSpectrum = None
    integration_time_micros = None
    wavelengths = None
    spectrum_length = None
    max = None
