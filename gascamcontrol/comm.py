import asyncio
import logging
import json
import aiohttp
from aiohttp import web
import configargparse


def _setup():
    """Do setup that needs to happen once on import."""
    parser = configargparse.get_argument_parser()
    parser.add("--port", default="8080", help="Port for websocket interface.")

    # wipe function to make sure it only runs once
    _setup.__code__ = (lambda: None).__code__


_setup()


class Comm():
    """Provide a bi-directional network interface."""

    def __init__(self):
        self.app = None
        self.logger = logging.getLogger(__name__)
        self.loop = asyncio.get_event_loop()
        self.websockets = []

    async def websocket_handler(self, request):
        """Handle websocket communication."""
        websocket = web.WebSocketResponse()
        await websocket.prepare(request)
        self.websockets.append(websocket)

        async for msg in websocket:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await websocket.close()
                else:
                    ans = msg.data + '/answer'
                    self.logger.info("got msg %s, answered %s", msg.data, ans)
                    # await websocket.send_str(ans)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                self.logger.info('ws connection closed with exception %s',
                                 websocket.exception())

        self.logger.info('websocket connection closed')

        return websocket

    async def send(self, item):
        """Send data to all clients."""
        for websocket in self.websockets:
            meta = item.meta
            meta["date"] = str(meta["date"])

            metab = bytes(json.dumps(meta), "utf-8")
            meta_len = bytes(str(len(metab)).rjust(4), "utf-8")
            data = meta_len + metab + item.data.tobytes()

            await websocket.send_bytes(data)
            self.logger.debug("bytes send %i %s", len(data),
                              str(len(metab)).rjust(4))

    @staticmethod
    def serve_display(app):
        """Server static webapp."""
        app.router.add_static('/app', 'webapp', show_index=True)

    def run(self):
        """Start running server and websocket."""
        app = web.Application()

        app.add_routes([web.get('/ws', self.websocket_handler)])
        self.serve_display(app)

        self.logger.info("run comm")

        runner = web.AppRunner(app)
        self.loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner)
        self.loop.run_until_complete(site.start())
