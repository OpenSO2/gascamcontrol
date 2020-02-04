"""Manage spectrometer shutter."""
import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import configargparse


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    # spectrometer shutter device descriptor
    # eg.
    # windows
    #     \\\\.\\COM6
    #     \\\\.\\USBSER000
    # linux
    #     /dev/serial/by-id/usb-Pololu_Corporation_Pololu_Micro_Maestro_6-Servo_
    #                       Controller_00135615-if00";
    #     /dev/ttyACM3
    # parser.add("--spectrometer_shutter_device",
    #            default="/dev/serial/by-id/usb-Pololu_Corporation"
    #            "_Pololu_Micro_Maestro_6-Servo_Controller_00135615-if00",
    #            help="spectrometer shutter device descriptor")

    # spectrometer shutter device channel - used for the pololu maestro
    # servo controller
    # parser.add("--spectrometer_shutter_channel", default=5)

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Spectrometershutter():
    """
    Delegates the actual implementation to the drivers in ./drivers.
    """

    def __init__(self, driver, device, channel):
        self.drivername = driver
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('myLog')

        driver = f"devices.spectrometershutter.drivers.{self.drivername}.spectrometershutter"
        self.driver = importlib.import_module(driver)
        self.spectrometershutter = self.driver.camerashutter()
        self.spectrometershutter.device = device
        self.spectrometershutter.channel = channel

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate spectrometer shutter device."""
        st = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                             self.driver.init, self.spectrometershutter)
        print("inited", self.spectrometershutter, self.spectrometershutter.device)
        if st:
            print("ERRROROROR!")
            print(f"fff {st}")
        return self

    async def setState(self, state):
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.setState,
                                        self.spectrometershutter, state)

    async def stop(self):
        """Stop spectrometer shutter and release device."""
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.uninit,
                                        self.spectrometershutter)
