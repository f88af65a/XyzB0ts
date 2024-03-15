import asyncio
import os
import time

from ujson import loads

from .Module import Module
from .util.BotPluginsManager import BotPluginsManager
from .util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from .util.Error import asyncTraceBack, debugPrint, printTraceBack
from .util.TimeTest import asyncTimeTest
from .util.Tool import getAttrFromModule


class BotRoute(Module):
    def init(self):
        self.pluginsManager = BotPluginsManager()
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]

    @asyncTraceBack
    @asyncTimeTest
    async def runInLoop(self):
        # 将Router信息同步至keeper
        await self.keeper.Set(
            f"/BotProcess/{os.getpid()}",
            {
                "type": "BotRouter",
                "startTime": str(int(time.time()))
            }
        )
        debugPrint('''BotRouter同步至keeper成功''', fromName="BotRouter")
        while True:
            # Route
            msg = await self.mq.AsyncFetchMessage(
                "RouteQueue"
            )
            if msg is None:
                continue
            msg = loads(msg.decode())
            if "code" not in msg:
                debugPrint("MSG中缺少code", fromName="BotRoute")
                continue
            if msg["code"] == 1:
                self.exit()
            if "data" not in msg:
                debugPrint("MSG中缺少data", fromName="BotRoute")
                continue
            msg = msg["data"]
            request = getAttrFromModule(
                    msg[0]["botPath"],
                    msg[0]["botType"]
                )(msg[0], msg[1])
            debugPrint(f"成功收到消息:{request.getUuid()}", fromName="BotRoute")
            asyncio.run_coroutine_threadsafe(
                self.routeRequest(request),
                self.loop
            )

    @asyncTimeTest
    async def routeRequest(self, request):
        for i in self.router:
            try:
                if (re := await i.route(
                        self.pluginsManager,
                        self,
                        request
                        )) and re[0] is False:
                    debugPrint(
                        f"消息:{request.getUuid()},"
                        f"被{i}:{re[1]}拦截"
                    )
                    break
            except Exception:
                printTraceBack()
                break

    def getBot(self):
        return self.bot

    async def run(self):
        await self.runInLoop()
