import pathlib
import random
import time


def init(spectro):
    """Find and init spectrometer."""
    path = pathlib.Path(__file__).parent.absolute()

    with open(f"{path}/fixtures/wavelengths.dat") as f:
        spectro.wavelengths = [float(wvl) for wvl in f]

    with open(f"{path}/fixtures/spectrum.dat") as f:
        spectro._lastSpectrum = [float(val) for val in f]

    spectro.spectrum_length = len(spectro.wavelengths)
    spectro.max = 65535


def get(spectro):
    """Get a spectrum."""
    time.sleep(spectro.integration_time_micros/1E6)
    spectro.lastSpectrum = [v + random.randint(-1000, 1000)
                            for v in spectro._lastSpectrum]


def uninit(_spectro):
    """Tear down."""


class Spectrometer:  # pylint: disable=too-few-public-methods
    """Mock a spectrometer with artificial data."""

    spectrometer = None
    lastSpectrum = None
    integration_time_micros = None
    wavelengths = None
    spectrum_length = None
    max = None

    def __str__(self):
        return f"""spectrometer = {self.spectrometer},
                   lastSpectrum = {self.lastSpectrum},
                   integration_time_micros = {self.integration_time_micros}
                   len(wavelengths) = {len(self.wavelengths)}
                   spectrum_length = {self.spectrum_length}
                   max = {self.max}"""
