import asyncio
from aiohttp import web
import aiohttp
# from concurrent.futures import ThreadPoolExecutor
import logging
import websockets


class Comm():
    websocket = None

    def __init__(self):
        self.logger = None

    async def echo(self, websocket,):
        self.logger("echo comm")
        async for message in websocket:
            self.logger.info(f"received msg, return {message}")
            await websocket.send(message)

    async def start2(self):
        self.logger = logging.getLogger('myLog')
        self.logger.info("run comm")

        websockets.serve(self.echo, 'localhost', 8081)
        self.logger.info("running comm?")

    async def hello(self, websocket, path):
        name = await websocket.recv()
        self.logger.info(f"< {name}")

        greeting = f"Hello {name}!"

        await websocket.send(greeting)
        self.logger.info(f"> {greeting}")

    def start2(self):
        self.logger = logging.getLogger('myLog')
        self.logger.info("run comm")

        start_server = websockets.serve(self.hello, "localhost", 8080)
        self.logger.info("run comm")
        asyncio.get_event_loop().run_until_complete(start_server)
        # asyncio.get_event_loop().run_forever()

    async def websocket_handler(self, request):
        logger = logging.getLogger('myLog')

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    ans = msg.data + '/answer'
                    logger.info(f'got msg {msg.data}, answered {ans}')
                    await ws.send_str(ans)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.info('ws connection closed with exception %s' %
                            ws.exception())

        logger.info('websocket connection closed')

        return ws

    def run(self):
        app = web.Application()
        app.add_routes([web.get('/ws', self.websocket_handler)])

        logger = logging.getLogger('myLog')
        logger.info("run comm")

        loop = asyncio.get_event_loop()
        runner = web.AppRunner(app)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner)
        loop.run_until_complete(site.start())
