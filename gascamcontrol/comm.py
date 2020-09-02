import asyncio
import logging
import json
import copy
import os
import aiohttp
from aiohttp import web
import configargparse
from .conf import Conf

# TODO:
#  - receive & change conf
#  - calc throughput


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()
    parser.add("--port", default="8080", help="Port for websocket interface.")

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Comm:
    """Provide a bi-directional network interface."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.loop = asyncio.get_event_loop()
        self.websockets = {
            "images": [],
            "viscam": [],
            "spec": [],
            "conf": []
        }  # all open socket connections
        self.options = Conf().options
        self.site = None

        self.app = web.Application()
        self.app.add_routes([web.get('/ws/{resource}', self.ws_handler)])
        path = os.path.dirname(os.path.abspath(__file__))
        self.app.router.add_static('/app', f'{path}/webapp', show_index=True)

    async def ws_handler(self, request):
        """Handle websocket communication."""
        websocket = web.WebSocketResponse()
        await websocket.prepare(request)
        resource = request.match_info['resource']
        self.websockets[resource].append(websocket)

        if resource == "conf":
            await websocket.send_json(self.options)

        try:
            async for msg in websocket:
                if msg.type == aiohttp.WSMsgType.ERROR:
                    self.logger.info('ws connection closed with exception %s',
                                     websocket.exception())
                    self.websockets[resource].remove(websocket)
        finally:
            await websocket.close()
            self.websockets[resource].remove(websocket)

        self.logger.info('websocket connection closed')

        return websocket

    async def send(self, item):
        """Send data to all subscribed clients."""
        item = copy.deepcopy(item)
        for websocket in self.websockets[item.type]:
            meta = item.meta
            meta["date"] = str(meta["date"])
            metab = bytes(json.dumps(meta), "utf-8")
            meta_len = bytes(str(len(metab)).rjust(4), "utf-8")
            data = meta_len + metab + item.data.tobytes()

            await websocket.send_bytes(data)
            self.logger.debug("bytes send %i %s", len(data),
                              str(len(metab)).rjust(4))

    def run(self):
        """Start running server and websocket."""
        runner = web.AppRunner(self.app)
        task = self.loop.create_task(runner.setup())
        self.loop.run_until_complete(task)

        port = self.options.port if "port" in self.options else None
        self.site = web.TCPSite(runner, port=port)
        self.loop.run_until_complete(self.site.start())

        self.logger.info("Serving on port %s", self.options.port)

    async def stop(self):
        """Stop and clean up server, disconnect socket clients."""
        self.logger.warning("stopping comm")
        await self.site.stop()
        await self.app.shutdown()
        await self.app.cleanup()
