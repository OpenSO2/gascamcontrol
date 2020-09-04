import unittest
from gascamcontrol.devicemanager import Devicemanager
from gascamcontrol.conf import Conf


class TestDevicemanager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        config = Conf()
        config.parse([])

    async def test_start_stop(self):
        devices = Devicemanager()
        devices.start()
        assert len(devices.running_tasks) > 0
        await devices.stop()
        assert len(devices.running_tasks) == 0
