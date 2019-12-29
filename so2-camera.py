import asyncio
import signal
import log
import tui
import conf
import ioo as io
import comm
from devices.viscam.viscam import Viscam
import devices.camera.cameras as cameras


class so2cam():
    """Setup basic plumbing."""

    def __init__(self):
        # self.cameras = cameras
        self.log = log.Log('myLog')
        self.conf = conf.Conf()
        # self.conf.parse()
        self.tui = tui.Tui()
        self.io = io.Io()
        self.comm = comm.Comm()
        # self.display = display.Display()

    def __enter__(self):
        # self.cameras.init()
        return self

    def __exit__(self, *args):
        # self.cameras.uninit()
        pass

    async def bullshit_logger(self):
        self.tui.update()

        while True:
            try:
                await asyncio.sleep(1)
                self.log.info("log")
                self.log.warning("warning")
                self.log.error("hey")
            except asyncio.CancelledError:
                print("Got CancelledError bullshit_logger")
                break

    async def monitor_cameras(self, loop):
        # import logging
        # logger = logging.getLogger('myLog')
        self.log.info("init cam done")
        await cams.init(loop)

        while True:
            try:
                await asyncio.sleep(3)
                cam = await cams.start(self.loop)
                import numpy as np
                self.log.info(f"shape received {np.shape(cam)}")
                # self.log.warning(f"cam res {cam[100:200]}")

                await self.comm.send(cam)

                await self.io.save_png("test.png", cam, loop)
            except asyncio.CancelledError:
                self.log.warning("Got CancelledError monitor_cameras")
                break

    async def monitor_viscam(self):
        self.log.info("init viscam")
        driver = "mock"

        async with Viscam(driver=driver) as viscam:
            while True:
                try:
                    img = await viscam.get()
                except asyncio.CancelledError:
                    self.log.warning("Got CancelledError monitor_viscam")
                    break

    async def monitor_kbd(self, loop):
        while True:
            try:
                await asyncio.sleep(.1)
                # if conf.options["stop"]:
                #     print("== stop")
                #     asyncio.create_task(self.shutdown(loop))
                #     print("== die!")
                #     break
            except asyncio.CancelledError:
                print("Got CancelledError monitor_kbd")
                break

    def shutdown(self, loop):
        self.log.info('received stop signal, cancelling tasks...')

        # Find all running tasks:
        pending = asyncio.Task.all_tasks()

        for task in pending:
            print('cancel task {}'.format(task))
            task.cancel()
            print('canceled')

        print("tasks canceled, closing loop")

        # Run loop until tasks done:
        print("\n run_until_complete")
        print("\n run_until_completed")
        # loop.close()
        loop.stop()

        print("loop closed")

    async def monitor_tui(self):
        while True:
            try:
                await asyncio.sleep(.1)
                self.tui.update()
            # self.tui.update()
            except asyncio.CancelledError:
                print("Got CancelledError tui")
                break

    def startup(self):
        self.conf.parse()
        self.tui.startup()

        loop = asyncio.get_event_loop()
        # loop.create_task(self.bullshit_logger())
        loop.create_task(self.monitor_kbd(loop))
        loop.create_task(self.monitor_tui())
        loop.create_task(self.monitor_cameras(loop))
        loop.create_task(self.monitor_viscam())
        self.comm.run()
        # self.display.run()

        self.loop = loop

        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(self.shutdown(loop)))

        try:
            loop.run_forever()
        finally:
            print("Closing Loop")
            loop.close()


if __name__ == '__main__':
    # with cameras.Cameras() as cams, tui.Tui() as tui, so2cam() as cam:
    with cameras.Cameras() as cams, so2cam() as cam:
        # with tui.Tui() as tui, so2cam() as cam:
        cam.startup()
