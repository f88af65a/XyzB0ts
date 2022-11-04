import ujson as json
import aiohttp
import zlib

import botsdk.util.HttpRequest
from botsdk.BotModule.Adapter import Adapter
from botsdk.util.Error import printTraceBack


class KaiheilaAdapter(Adapter):
    def init(self, data):
        self.url = data["path"]
        self.data["headers"] = {
            "Content-type": "application/json",
            "Authorization": (f"""{data["authorizationType"]}"""
                              f""" {data["token"]}""")
            }
        self.session = None

    async def wsConnect(self, url, timeout=15):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        timeout = aiohttp.ClientTimeout(total=timeout)
        try:
            self.ws = await self.session.ws_connect(
                url, headers=self.data["headers"], timeout=timeout,
                verify_ssl=False)
            return 0
        except Exception:
            printTraceBack()
            return None

    async def wsDisconnect(self):
        if not self.wsClosed():
            await self.ws.close()

    async def wsRecv(self, timeout=15):
        if not self.wsClosed():
            try:
                return json.loads(zlib.decompress(
                    await self.ws.receive_bytes(timeout=timeout)))
            except Exception:
                pass
        return None

    async def wsSend(self, data):
        if not self.wsClosed():
            try:
                return await self.ws.send_json(data)
            except Exception:
                printTraceBack()
        return None

    def wsClosed(self):
        return self.ws.closed

    async def get(self, parameter, **kwargs):
        return json.loads(
            await botsdk.util.HttpRequest.get(
                (self.url + parameter["path"] + "?"
                 + "&".join(["=".join([i, kwargs[i]]) for i in kwargs])),
                headers=self.data["headers"]))

    async def post(self, parameter, **kwargs):
        for i in kwargs:
            if kwargs[i] is None:
                del kwargs[i]
        return json.loads(
            await botsdk.util.HttpRequest.post(
                self.url + parameter["path"], kwargs,
                headers=self.data["headers"]))
