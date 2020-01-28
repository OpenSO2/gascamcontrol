from seabreeze.spectrometers import Spectrometer


SPEC = None


def init(spectro):
    global SPEC
    SPEC = Spectrometer.from_first_available()

    spectro.wavelengths = SPEC.wavelengths()
    spectro.spectrum_length = len(spectro.wavelengths)
    spectro.max = 65535


def get(spectro):
    global SPEC
    SPEC.integration_time_micros(spectro.integration_time_micros)
    spectro.lastSpectrum = SPEC.intensities()


def uninit(_spectro):
    global SPEC
    SPEC = None


class spectrometer():
    lastSpectrum = None
    integration_time_micros = None
    wavelengths = None
    spectrum_length = None
    max = None
