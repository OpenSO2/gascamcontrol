"""Manage a global fifo queue system for data received from sensors."""
import asyncio
import logging

# meta
#   type eg 310, 330
#   date
#   gps
#   temperature
#   orientation
#   exposure
#   enhance
#   depth
#   width
#   height
# data


class Queue():
    """Manage tasks to run (eg. writing to disk etc)."""

    __monostate = None  # borg pattern

    def __init__(self):
        if Queue.__monostate:
            self.__dict__ = Queue.__monostate
        else:
            Queue.__monostate = self.__dict__

            self.queue = asyncio.Queue()
            self.logging = logging.getLogger(__name__)

    def __len__(self):
        return self.queue.qsize()

    async def push(self, task):
        """Queue task."""
        await self.queue.put(task)
        self.logging.info("add task to queue qsize %s %s",
                          self.queue.qsize(), len(self))

    async def pop(self):
        """Retrieve highest priority task from queue."""
        return await self.queue.get()

    async def join(self):
        """Wait for queue to be emptied (blocking)."""
        await self.queue.join()


class QueueItem:  # pylint: disable=R0903
    """Wrap data that has been queued for processing."""

    def __init__(self, data, meta):
        self.data = data
        self.meta = meta


class CamQueueItem(QueueItem):  # pylint: disable=R0903
    """Container for camera image."""


class ViscamQueueItem(QueueItem):  # pylint: disable=R0903
    """Container for viscam image."""


class SpecQueueItem(QueueItem):  # pylint: disable=R0903
    """Container for Spectrogram."""

    def __init__(self, wavelengths, spectrum, meta):
        super().__init__(zip(wavelengths, spectrum), meta)

    # def __init__(self, data, meta):
    #     self.data = data
    #     self.meta = meta
