import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import configargparse


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()

    # camerashutter_device = \\\\.\\COM22
    parser.add("--camerashutter_device", default="/dev/serial/by-id/usb"
               "-FTDI_FT232R_USB_UART_A402X19O-if00-port0",
               help="camera shutter device descriptor")

    parser.add("--camerashutter_driver", default="mock",
               help="Driver for camera shutter device")

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Camerashutter:
    """Device to block light to the camera(s) for dark image correction.

    Delegates the actual implementation to the drivers in ./drivers.
    """

    def __init__(self, driver, device):
        self.drivername = driver
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger(__name__)

        print(__name__, __package__)

        driver = f".drivers.{driver}.camerashutter"
        self.driver = importlib.import_module(driver, package=__package__)
        self.camerashutter = self.driver.camerashutter()
        self.camerashutter.device = device

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate camera shutter device."""
        status = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                                 self.driver.init,
                                                 self.camerashutter)

        # FIXME
        if status:
            print("ERRROROROR!")
        return self

    async def set_state(self, state):
        """Set state of shutter, either 'open' or 'closed'."""
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.set_state,
                                        self.camerashutter, state)

    async def open(self):
        """Open shutter."""
        await self.set_state("open")

    async def close(self):
        """Close shutter."""
        await self.set_state("close")

    async def stop(self):
        """Stop viscam and release device."""
        await self.loop.run_in_executor(ThreadPoolExecutor(),
                                        self.driver.uninit, self.camerashutter)
