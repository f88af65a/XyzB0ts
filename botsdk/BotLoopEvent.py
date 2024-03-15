import asyncio
import os
import threading
import time

from ujson import loads

from .Module import Module
from .util.BotPluginsManager import BotPluginsManager
from .util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from .util.Error import asyncTraceBack, debugPrint, printTraceBack
from .util.TimeTest import asyncTimeTest


class BotLoopEvent(Module):
    def init(self):
        self.pluginsManager = BotPluginsManager()
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]

    @asyncTraceBack
    @asyncTimeTest
    async def runInLoop(self):
        # 将LoopEvent信息同步至keeper
        await self.keeper.Set(
            f"/BotProcess/{os.getpid()}",
            {
                "type": "BotLoopEvent",
                "startTime": str(int(time.time()))
            }
        )
        await self.keeper.Set(
            "/BotFlags/BotLoopEvent",
            {
                "type": "BotLoopEvent",
                "startTime": str(int(time.time()))
            }
        )
        debugPrint('''BotLoopEvent同步至keeper成功''', fromName="BotLoopEvent")
        # LoopEvent
        try:
            plugins = self.pluginsManager.getAllPlugin()
            for i in plugins:
                events = i.getLoopEvent()
                for j in events:
                    asyncio.run_coroutine_threadsafe(
                        j[0](*j[1], **j[2]),
                        self.loop
                    )
        except Exception:
            printTraceBack()
            debugPrint("加载时出错", fromName="BotLoopEvent")
            self.exit()
        debugPrint("LoopEvent加载完成", fromName="BotLoopEvent")

    async def run(self):
        await self.runInLoop()
