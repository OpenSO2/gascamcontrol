import unittest
import sys
import os
sys.path.append(os.path.realpath(os.path.dirname(__file__)
                                 + "/../gascamcontrol"))

from devicemanager import Devicemanager  # noqa: E402,E501 pylint: disable=C0413,E0401
import conf  # noqa: E402,E501 pylint: disable=C0413,E0401


class TestDevicemanager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        config = conf.Conf()
        config.parse([])

    async def test_start_stop(self):
        devices = Devicemanager()
        devices.start()
        assert len(devices.running_tasks) > 0
        await devices.stop()
        assert len(devices.running_tasks) == 0
