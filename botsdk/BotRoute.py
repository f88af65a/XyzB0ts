import asyncio
from json import loads
import os
import time

from kazoo.exceptions import NodeExistsError

from confluent_kafka import Consumer

from botsdk.util.ZookeeperTool import AddEphemeralNode, GetZKClient

from .util.BotPluginsManager import BotPluginsManager
from .util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from .util.Error import asyncTraceBack, debugPrint, printTraceBack
from .util.TimeTest import asyncTimeTest
from .util.Tool import getAttrFromModule


class BotRoute:
    def __init__(self):
        self.pluginsManager = BotPluginsManager()
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]
        self.loopRouter = False

    @asyncTraceBack
    @asyncTimeTest
    async def route(self):
        # 将Router信息同步至Zookeeper
        if not AddEphemeralNode("/BotProcess", f"{os.getpid()}", {
                        "type": "BotRouter",
                        "startTime": str(int(time.time()))
                    }):
            debugPrint(
                    '''BotRouter同步至zookeeper失败''',
                    fromName="BotRouter")
            return
        debugPrint('''BotRouter同步至zookeeper成功''', fromName="BotRouter")
        c = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': "targetHandleGroup"
        })
        c.subscribe(['routeList'])
        while True:
            # loopEvent
            try:
                zk = GetZKClient()
                if not zk.exists("/BotFlags"):
                    try:
                        zk.create("/BotFlags")
                    except NodeExistsError:
                        pass
                    except Exception:
                        printTraceBack()
                        exit()
                if not zk.exists("/BotFlags/RouterLoopEvent"):
                    try:
                        zk.create(
                                "/BotFlags/RouterLoopEvent",
                                ephemeral=True)
                        self.loopRouter = True
                        plugins = self.pluginsManager.getAllPlugin()
                        for i in plugins:
                            events = i.getLoopEvent()
                            for j in events:
                                asyncio.run_coroutine_threadsafe(
                                        j[0](*j[1], **j[2]), self.loop)
                    except NodeExistsError:
                        pass
                    except Exception:
                        printTraceBack()
                        exit()
            except Exception:
                printTraceBack()
                exit()
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
                try:
                    c.close()
                except Exception:
                    pass
                try:
                    GetZKClient().stop()
                except Exception:
                    pass
                exit()
            if "data" not in msg:
                debugPrint("MSG中缺少data", fromName="BotRoute")
                continue
            msg = msg["data"]
            request = getAttrFromModule(
                    msg[0]["botPath"],
                    msg[0]["botType"]
                )(msg[0], msg[1])
            for i in range(len(self.router)):
                if (re := await self.router[i].route(
                        self.pluginsManager, request
                        )) is not None and re is False:
                    break
            await asyncio.sleep(0)

    def getBot(self):
        return self.bot

    def isLoopRouter(self):
        return self.loopRouter

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.run_coroutine_threadsafe(self.route(), self.loop)
        self.loop.run_forever()
