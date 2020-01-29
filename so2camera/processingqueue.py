"""Manage a global fifo queue system for data received from sensors."""
import asyncio
import logging


class Queue():
    """Manage tasks to run (eg. writing to disk etc)."""

    __monostate = None  # borg pattern

    def __init__(self):
        if Queue.__monostate:
            self.__dict__ = Queue.__monostate
        else:
            Queue.__monostate = self.__dict__

            self.queue = asyncio.Queue()
            self.logging = logging.getLogger("myLog")

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

    def join(self):
        """Wait for queue to be emptied (blocking)."""
        self.queue.join()


class QueueItem():
    """Wrap data that has been queued for processing."""

    def __init__(self, data, meta):
        self.data = data
        self.meta = meta


class CamQueueItem(QueueItem):
    def __init_(self, image, meta):
        QueueItem.__init__(self, image, meta)


class ViscamQueueItem(QueueItem):
    def __init_(self, image, meta):
        QueueItem.__init__(self, image, meta)


class SpecQueueItem(QueueItem):
    pass

# class CamSet(QueueItem):
#     def __init_(self, meta, data):
#         QueueItem.__init__(self)
#         self.meta = meta
#         self.data = data
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
