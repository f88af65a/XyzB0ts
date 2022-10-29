import asyncio
import os
import threading
import time
from json import loads

from confluent_kafka import Consumer

from botsdk.util.ZookeeperTool import AddEphemeralNode, GetZKClient

from .util.BotPluginsManager import BotPluginsManager
from .util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from .util.Error import asyncTraceBack, debugPrint, printTraceBack
from .util.TimeTest import asyncTimeTest


class BotLoopEvent:
    def __init__(self):
        self.pluginsManager = BotPluginsManager()
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]

    @asyncTraceBack
    @asyncTimeTest
    async def loop(self):
        # 将LoopEvent信息同步至Zookeeper
        if not AddEphemeralNode("/BotProcess", f"{os.getpid()}", {
                        "type": "BotLoopEvent",
                        "startTime": str(int(time.time()))
                    }):
            debugPrint(
                    '''BotLoopEvent同步至zookeeper失败''',
                    fromName="BotLoopEvent")
            GetZKClient().stop()
            exit()
        if not AddEphemeralNode("/BotFlags", "BotLoopEvent"):
            debugPrint(
                    '''BotLoopEvent同步至zookeeper失败''',
                    fromName="BotLoopEvent")
            GetZKClient().stop()
            exit()
        thread = threading.Thread(target=self.kafkaThread)
        thread.start()
        debugPrint('''BotLoopEvent同步至zookeeper成功''', fromName="BotLoopEvent")
        while True:
            # LoopEvent
            try:
                plugins = self.pluginsManager.getAllPlugin()
                for i in plugins:
                    events = i.getLoopEvent()
                    for j in events:
                        await j[0](*j[1], **j[2])
            except Exception:
                printTraceBack()

    def kafkaThread(self):
        c = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': "LoopEventGroup"
        })
        c.subscribe(['BotLoopEvent'])
        while True:
            msg = self.c.poll(1.0)
            if msg is not None and not msg.error():
                msg = loads(msg.value())
                if "code" not in msg:
                    debugPrint("MSG缺少code", fromName="BotService")
                else:
                    if msg["code"] == 1:
                        self.c.close()
                        GetZKClient().stop()
                        exit()

    def run(self):
        asyncio.run(self.loop())
