import asyncio
from json import loads
import os
import time

from confluent_kafka import Consumer

from botsdk.util.ZookeeperTool import AddEphemeralNode

from .util.BotPluginsManager import BotPluginsManager
from .util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from .util.Error import asyncTraceBack, debugPrint
from .util.TimeTest import asyncTimeTest
from .util.Tool import getAttrFromModule


class BotRoute:
    def __init__(self):
        self.pluginsManager = BotPluginsManager()
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]

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
        c = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': "targetHandleGroup"
        })
        c.subscribe(['routeList'])
        while True:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                debugPrint(msg.error())
                continue
            msg = loads(msg.value())
            request = getAttrFromModule(
                    msg[0]["botPath"],
                    msg[0]["botType"]
                )(msg[0], msg[1])
            for i in range(len(self.router)):
                if (re := await self.router[i].route(
                        self.pluginsManager, request,
                        None)) is not None and re is False:
                    break
            await asyncio.sleep(0)

    def getBot(self):
        return self.bot

    def run(self):
        asyncio.run(self.route())
