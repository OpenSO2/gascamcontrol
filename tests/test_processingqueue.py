import unittest
from gascamcontrol.processingqueue import Queue, QueueItem


class TestQueueItem(unittest.TestCase):
    def test_invalid_queueItem(self):
        self.assertRaises(TypeError, QueueItem)


class TestQueue(unittest.IsolatedAsyncioTestCase):
    async def test_queue_push_pop(self):
        q = Queue()
        item = QueueItem({}, {})
        assert len(q) == 0

        await q.push(item)
        assert len(q) == 1

        popped_item = await q.pop()
        assert len(q) == 0

        assert(item == popped_item)
