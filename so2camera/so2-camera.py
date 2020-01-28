import asyncio
import signal
import logging
import log
import tui
import conf
import diskmanager
import comm
import devicemanager
from processingqueue import Queue


class so2cam():
    """Setup basic plumbing."""

    def __init__(self):
        self.conf = conf.Conf()
        self.conf.parse()

        log.Log('myLog')

        self.logging = logging.getLogger("myLog")
        self.tui = tui.Tui()
        self.diskmanager = diskmanager.Diskmanager()
        self.comm = comm.Comm()
        # self.display = display.Display()
        self.queue = Queue()
        self.loop = asyncio.get_event_loop()
        self.devices = devicemanager.Devicemanager()

    async def consume_queue(self):
        """Process items from queue."""
        self.logging.info("consume_queue")
        while True:
            self.logging.info("queue pop")
            item = await self.queue.pop()

            self.logging.debug('processed item %s...', item)

            await self.comm.send(item)
            await self.diskmanager.save(item)

    async def monitor_kbd(self):
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

    def shutdown(self):
        self.logging.info('received stop signal, cancelling tasks...')

        self.devices.stop()

        # Find all running tasks:
        pending = asyncio.Task.all_tasks()

        for task in pending:
            self.logging.info('cancel task %s', task)
            task.cancel()
            self.logging.info('canceled')

        self.logging.info("tasks canceled, closing loop")

        # Run loop until tasks done:
        self.logging.info("\n run_until_complete")
        # loop.close()
        self.loop.stop()

        self.queue.join()

        self.logging.info("loop closed")

    async def monitor_tui(self):
        while True:
            try:
                await asyncio.sleep(1)
                self.tui.update()

            except asyncio.CancelledError:
                self.logging.info("Got CancelledError tui")
                break

    def startup(self):
        self.tui.startup()
        self.loop.create_task(self.monitor_kbd())
        self.loop.create_task(self.monitor_tui())
        self.logging.info("consume queue:")
        self.loop.create_task(self.consume_queue())
        self.logging.info("consume queue task started")
        self.comm.run()
        # self.display.run()

        # signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        # for sign in signals:
        #     self.loop.add_signal_handler(
        #         sign, lambda s=s: asyncio.create_task(self.shutdown()))

        self.devices.start()

        try:
            self.loop.run_forever()
        finally:
            print("Closing Loop")
            self.loop.close()


def main():
    """Kick of program."""
    cam = so2cam()
    cam.startup()


if __name__ == '__main__':
    main()
