import unittest
import sys
import os
import json
from datetime import datetime
from argparse import Namespace
import pytest
from dateutil.parser import parse
import numpy as np
import aiohttp
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
sys.path.append(os.path.realpath(os.path.dirname(__file__)
                                 + "/../gascamcontrol"))

from comm import Comm  # noqa: E402,E501 pylint: disable=C0413,E0401
from processingqueue import CamQueueItem, ViscamQueueItem, SpecQueueItem  # noqa: E402,E501 pylint: disable=C0413,E0401
import conf  # noqa: E402,E501 pylint: disable=C0413,E0401


class TestComm(AioHTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        print(self.server)
        print(self.server.port)

    async def get_application(self):
        self.comm = Comm()
        return self.comm.app

    @unittest_run_loop
    async def test_connect(self):
        assert len(self.comm.websockets["images"]) == 0
        async with self.client.ws_connect("/ws/images"):
            assert len(self.comm.websockets["images"]) == 1
        assert len(self.comm.websockets["images"]) == 0

    @unittest_run_loop
    async def test_send_image(self):
        meta = {"date": datetime.now()}
        img = np.array([0, 1, 3, 4, 5])
        item = CamQueueItem(img, meta)
        async with self.client.ws_connect("/ws/images") as ws:
            await self.comm.send(item)
            received = await ws.receive_bytes()
            metalength = int(received[1:4])
            meta_received_b = received[4:4 + metalength]
            data = received[4 + metalength:]
            meta_received = json.loads(meta_received_b)
            assert meta["date"] == parse(meta_received["date"])
            assert (np.frombuffer(data, dtype=int) == img).all()

    @unittest_run_loop
    async def test_viscam(self):
        meta = {"date": datetime.now()}
        img = np.array([0, 1, 3, 4, 5])
        item = ViscamQueueItem(img, meta)
        async with self.client.ws_connect("/ws/viscam") as ws:
            await self.comm.send(item)
            received = await ws.receive_bytes()
            metalength = int(received[1:4])
            meta_received_b = received[4:4 + metalength]
            data = received[4 + metalength:]
            meta_received = json.loads(meta_received_b)
            assert meta["date"] == parse(meta_received["date"])
            assert (np.frombuffer(data, dtype=int) == img).all()

    @unittest_run_loop
    async def test_spec(self):
        meta = {"date": datetime.now()}
        spec = np.array([0, 1, 3, 4, 5])
        wvl = np.array([0, 1, 3, 4, 5])
        item = SpecQueueItem(wvl, spec, meta)
        async with self.client.ws_connect("/ws/spec") as ws:
            await self.comm.send(item)
            received = await ws.receive_bytes()
            metalength = int(received[1:4])
            meta_received_b = received[4:4 + metalength]
            data = received[4 + metalength:]
            meta_received = json.loads(meta_received_b)
            assert meta["date"] == parse(meta_received["date"])
            dat = np.frombuffer(data, dtype=int)
            dat = dat.reshape((len(dat)//2, 2))
            assert (dat == np.dstack((wvl, spec))).all()

#    @unittest_run_loop
#    @unittest.skip
#    async def test_stats(self):
#        async with self.client.ws_connect("/ws/stats") as ws:
#            await self.comm.send(item)

    @unittest_run_loop
    async def test_conf(self):
        async with self.client.ws_connect("/ws/conf") as ws:
            conf = await ws.receive_json()
            assert type(conf) == dict

    @unittest_run_loop
    async def test_static(self):
        resp = await self.client.request("GET", "app")
        assert resp.status == 200


class TestCommPort(unittest.IsolatedAsyncioTestCase):
    port = 8082

    def setUp(self) -> None:
        conf.Conf().options = Namespace(port=self.port)
        self.url = f'http://localhost:{self.port}/ws/images'
        self.comm = Comm()
        self.comm.run()

    async def asyncTearDown(self) -> None:
        await self.comm.stop()

    async def test_port(self):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.url):
                assert len(self.comm.websockets["images"]) == 1

    async def test_multiple_connections(self):
        async with aiohttp.ClientSession() as session1:
            async with session1.ws_connect(self.url):
                assert len(self.comm.websockets["images"]) == 1

                async with aiohttp.ClientSession() as session2:
                    async with session2.ws_connect(self.url):
                        assert len(self.comm.websockets["images"]) == 2

                        async with aiohttp.ClientSession() as session3:
                            async with session3.ws_connect(self.url):
                                assert len(self.comm.websockets["images"]) == 3

        assert len(self.comm.websockets["images"]) == 0


class TestCommFailToStart(unittest.IsolatedAsyncioTestCase):
    port = 1

    def setUp(self) -> None:
        conf.Conf().options = Namespace(port=self.port)

    async def test_fail_on_invalid_port(self):
        self.comm = Comm()
        with pytest.raises(Exception):
            self.comm.run()
