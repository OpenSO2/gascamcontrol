from aiohttp import web
import aiohttp
# from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging

a = {
    'app': None
}

class Comm():
    def __init__(self):
        self.app = None
        self.logger = logging.getLogger('myLog')

    websockets = []

    async def websocket_handler(self, request):
        logger = logging.getLogger('myLog')

        websocket = web.WebSocketResponse()
        await websocket.prepare(request)
        self.websockets.append(websocket)

        async for msg in websocket:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await websocket.close()
                else:
                    ans = msg.data + '/answer'
                    logger.info("got msg %s, answered %s", msg.data, ans)
                    # await websocket.send_str(ans)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.info('ws connection closed with exception %s',
                            websocket.exception())

        logger.info('websocket connection closed')

        return websocket

    async def send(self, img):
        for websocket in self.websockets:
            # if "send" in websocket:
            # await websocket.send_str(f"img shape {img.shape}")
            # await websocket.send_bytes(img.tobytes())
            logger = logging.getLogger('myLog')
            logger.info("send data")
            img *= 16
            # logger.info(str(img.tolist()))
            await websocket.send_bytes(img.tobytes())

    def serve_display(self, app):
        app.router.add_static('/app', 'webapp', show_index=True)

    def run(self):
        app = web.Application()

        app.add_routes([web.get('/ws', self.websocket_handler)])
        self.serve_display(app)

        self.logger.info("run comm")

        loop = asyncio.get_event_loop()
        runner = web.AppRunner(app)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner)
        loop.run_until_complete(site.start())
