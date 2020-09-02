"""Manage spectrometer shutter."""
import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from ...exceptions import InitError
import configargparse
from ...conf import Conf


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    parser.add_argument("--driver", default="mock",
                        help="Device driver to use (see ./drivers)")

    # spectrometer shutter device descriptor
    # eg.
    # windows
    #     \\\\.\\COM6
    #     \\\\.\\USBSER000
    # linux
    #     /dev/serial/by-id/usb-Pololu_Corporation_Pololu_Micro_Maestro_6-Servo_
    #                       Controller_00135615-if00";
    #     /dev/ttyACM3
    parser.add("--spectrometer_shutter_device",
               default="/dev/serial/by-id/usb-Pololu_Corporation_Pololu"
                       "_Micro_Maestro_6-Servo_Controller_00135615-if00",
               help="spectrometer shutter device descriptor")
    parser.add("--spectrometer_shutter_driver",
               default="mock",
               help="spectrometer shutter driver")
    # spectrometer shutter device channel - used for the pololu maestro
    # servo controller
    parser.add("--spectrometer_shutter_channel", default=5)

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Spectrometershutter:
    """Implement shutter device for spectrometer.

    Delegates the actual implementation to the drivers in ./drivers.
    """

    def __init__(self, driver=None):
        self.options = Conf().options
        self.drivername = driver or self.options.spectrometer_shutter_driver
        self.loop = asyncio.get_event_loop()
        self.logging = logging.getLogger(__name__)

        driver = f".drivers.{self.drivername}.spectrometershutter"
        self.driver = importlib.import_module(driver, package=__package__)
        self.spectrometershutter = self.driver.camerashutter()
        self.spectrometershutter.device = \
            self.options.spectrometer_shutter_device
        self.spectrometershutter.channel = \
            self.options.spectrometer_shutter_channel

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate spectrometer shutter device."""
        status = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                                 self.driver.init,
                                                 self.spectrometershutter)
        if status:
            raise InitError("Can't init spectrometer shutter.")

        self.logging.debug("inited %s %s", self.spectrometershutter,
                           self.spectrometershutter.device)

    async def set_state(self, state):
        """Set state of shutter, either 'open' or 'closed'."""
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.set_state,
                                        self.spectrometershutter, state)

    async def stop(self):
        """Stop spectrometer shutter and release device."""
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.uninit,
                                        self.spectrometershutter)
