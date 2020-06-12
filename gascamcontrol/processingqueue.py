"""Manage a global fifo queue system for data received from sensors."""
import asyncio
import logging
import numpy as np

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


class Queue:
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
        self.logging.debug("add task to queue qsize %s %s",
                           self.queue.qsize(), len(self))

    async def pop(self):
        """Retrieve highest priority task from queue."""
        return await self.queue.get()

    async def join(self):
        """Wait for queue to be emptied (blocking)."""
        self.logging.debug("processing queue, %i items in queue",
                           self.queue.qsize())
        try:
            await asyncio.wait_for(self.queue.join(), timeout=5)
        except asyncio.TimeoutError:
            self.logging.error("queue timed out")


class QueueItem:  # pylint: disable=R0903
    """Wrap data that has been queued for processing."""

    def __init__(self, data, meta):
        self.data = data
        self.meta = meta
        self.type = None


class CamQueueItem(QueueItem):  # pylint: disable=R0903
    """Container for camera image."""

    def __init__(self, *args, **kwargs):
        super(CamQueueItem, self).__init__(*args, **kwargs)
        self.type = "images"


class ViscamQueueItem(QueueItem):  # pylint: disable=R0903
    """Container for viscam image."""

    def __init__(self, *args, **kwargs):
        super(ViscamQueueItem, self).__init__(*args, **kwargs)
        self.type = "viscam"


class SpecQueueItem(QueueItem):  # pylint: disable=R0903
    """Container for Spectrogram."""

    def __init__(self, wavelengths, spectrum, meta):
        data = np.dstack((wavelengths, spectrum))
        super(SpecQueueItem, self).__init__(data, meta)
        self.type = "spec"
