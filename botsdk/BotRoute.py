import asyncio
import os
import threading
import time

from confluent_kafka import Consumer
from ujson import loads

from .Module import Module
from .util.BotPluginsManager import BotPluginsManager
from .util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from .util.Error import asyncTraceBack, debugPrint, printTraceBack
from .util.TimeTest import asyncTimeTest
from .util.Tool import getAttrFromModule
from .util.ZookeeperTool import AddEphemeralNode, GetZKClient


class BotRoute(Module):
    def init(self):
        self.pluginsManager = BotPluginsManager()
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]

    @asyncTraceBack
    @asyncTimeTest
    async def runInLoop(self):
        # 将Router信息同步至Zookeeper
        if not AddEphemeralNode("/BotProcess", f"{os.getpid()}", {
                        "type": "BotRouter",
                        "startTime": str(int(time.time()))
                    }):
            debugPrint(
                    '''BotRouter同步至zookeeper失败''',
                    fromName="BotRouter")
            return
        self.addToExit(GetZKClient().stop)
        debugPrint('''BotRouter同步至zookeeper成功''', fromName="BotRouter")
        fetchMessageThread = threading.Thread(target=self.fetchMessageThread)
        fetchMessageThread.start()

    def fetchMessageThread(self):
        debugPrint('''消息获取线程启动''', fromName="BotRouter")
        c = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': "routeListGroup"
        })
        c.subscribe(['routeList'])
        self.addToExit(c.close)
        while True:
            # Route
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                debugPrint(msg.error())
                continue
            msg = loads(msg.value())
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
                    self.loop)

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
