import asyncio
import signal
import logging
import traceback
from .log import Log
from .tui import Tui
from .conf import Conf
from .diskmanager import Diskmanager
from .comm import Comm
from .devicemanager import Devicemanager
from .processingqueue import Queue
from .pluginmanager import Pluginmanager


class Gascamcontrol():
    """Setup basic plumbing."""

    def __init__(self):
        self.conf = Conf()
        self.conf.parse()
        self.options = self.conf.options

        self.logging = logging.getLogger(__name__)
        self.tui = Tui()
        self.diskmanager = Diskmanager()
        self.comm = Comm()
        # self.display = display.Display()
        self.queue = Queue()
        self.loop = asyncio.get_event_loop()
        self.devices = Devicemanager()
        self.pluginmanager = Pluginmanager()

    async def consume_queue(self):
        """Process items from queue."""
        self.logging.info("consume_queue")
        while True:
            self.logging.info("queue pop")
            item = await self.queue.pop()

            self.logging.debug('processed item %s...', item)

            await self.comm.send(item)
            await self.diskmanager.save(item)

#    async def monitor_kbd(self):
#        while True:
#            try:
#                await asyncio.sleep(.1)
#                # if conf.options["stop"]:
#                #     print("== stop")
#                #     asyncio.create_task(self.shutdown(loop))
#                #     print("== die!")
#                #     break
#            except asyncio.CancelledError:
#                print("Got CancelledError monitor_kbd")
#                break

    async def shutdown(self, sig=None):
        """Stop application, kill background tasks, stop devices, cleanup."""
        if sig:
            self.logging.info("Received exit signal %s", sig.name)

        self.logging.info("Shutting down...")

        await self.pluginmanager.uninit()
        await self.devices.stop()

        # Find all running tasks:
        pending = asyncio.all_tasks()
        pending.remove(asyncio.current_task())

        for task in pending:
            self.logging.info('cancel task %s', task)
            task.cancel()
            self.logging.info('canceled')

        self.logging.info("all tasks canceled")

        # Run loop until tasks done:
        self.logging.debug("empty work queue")
        await self.queue.join()

        if not self.options.simpletui:
            self.tui.restore()

        self.loop.stop()
        self.logging.info("shutdown complete")

    async def monitor_tui(self):
        """Update text user interface."""
        while True:
            try:
                await asyncio.sleep(1)
                self.tui.update()

            except asyncio.CancelledError:
                self.logging.info("Got CancelledError tui")
                break

    def handle_exception(self, _loop, context):
        """Shut down on asyncio exceptions and try to print a traceback."""
        self.logging.error("Caught exception: %s", context, exc_info=1)

        if "exception" in context:
            traceback.print_tb(context["exception"].__traceback__)

        self.loop.create_task(self.shutdown())

    def startup(self):
        """Start application."""
        if self.options.simpletui:
            Log().route_to_stdout()  # pylint: disable=no-member
        else:
            self.tui.startup()
            self.loop.create_task(self.monitor_tui())

        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for sig in signals:
            self.loop.add_signal_handler(
                sig, lambda sig=sig: asyncio.create_task(self.shutdown(sig)))
        self.loop.set_exception_handler(self.handle_exception)

        self.logging.info("consume queue:")
        self.loop.create_task(self.consume_queue())
        self.logging.info("consume queue task started")
        self.comm.run()
        # self.display.run()
        self.devices.start()

        self.loop.create_task(self.pluginmanager.init())
        self.loop.set_debug(self.options.debug)
        self.loop.run_forever()


def main():
    """Kick of program."""
    cam = Gascamcontrol()
    cam.startup()


if __name__ == '__main__':
    main()
