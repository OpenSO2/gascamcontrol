"""
"""
import importlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from log import stdout_redirector


class Camerashutter():
    """

    Delegates the actual implementation to the drivers in ./drivers.
    """

    def __init__(self, driver, device):
        self.drivername = driver
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('myLog')

        driver = f"devices.camerashutter.drivers.{self.drivername}.camerashutter"
        self.driver = importlib.import_module(driver)
        self.camerashutter = self.driver.camerashutter()
        self.camerashutter.device = device

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        """Initiate camera shutter device."""
        print("start")
        with stdout_redirector():
            st = await self.loop.run_in_executor(ThreadPoolExecutor(),
                                                 self.driver.init, self.camerashutter)
        print("inited")
        if st:
            print("ERRROROROR!")
            print(f"fff {st}")
            raise
        return self

    async def setState(self, state):
        """ """
        print("set")
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.setState,
                                            self.camerashutter, state)
        # return np.reshape(self.viscam.buffer, shape)

    async def stop(self):
        """Stop viscam and release device."""
        with stdout_redirector():
            await self.loop.run_in_executor(ThreadPoolExecutor(),
                                            self.driver.uninit, self.camerashutter)
