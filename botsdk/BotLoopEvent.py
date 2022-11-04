import asyncio
import os
import threading
import time
from ujson import loads

from confluent_kafka import Consumer

from .Module import Module
from .util.BotPluginsManager import BotPluginsManager
from .util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from .util.Error import asyncTraceBack, debugPrint, printTraceBack
from .util.TimeTest import asyncTimeTest
from .util.ZookeeperTool import AddEphemeralNode, GetZKClient


class BotLoopEvent(Module):
    def init(self):
        self.pluginsManager = BotPluginsManager()
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]

    @asyncTraceBack
    @asyncTimeTest
    async def loop(self):
        # 将LoopEvent信息同步至Zookeeper
        self.addToExit(GetZKClient().stop)
        if not AddEphemeralNode("/BotProcess", f"{os.getpid()}", {
                        "type": "BotLoopEvent",
                        "startTime": str(int(time.time()))
                    }):
            debugPrint(
                    '''BotLoopEvent同步至zookeeper失败''',
                    fromName="BotLoopEvent")
            self.exit()
        if not AddEphemeralNode("/BotFlags", "BotLoopEvent"):
            debugPrint(
                    '''建立唯一失败''',
                    fromName="BotLoopEvent")
            self.exit()
        debugPrint('''BotLoopEvent同步至zookeeper成功''', fromName="BotLoopEvent")
        '''
        thread = threading.Thread(target=self.kafkaThread)
        thread.start()
        '''
        # LoopEvent
        try:
            plugins = self.pluginsManager.getAllPlugin()
            for i in plugins:
                events = i.getLoopEvent()
                for j in events:
                    asyncio.run_coroutine_threadsafe(
                        j[0](*j[1], **j[2]),
                        self.asyncLoop
                    )
        except Exception:
            printTraceBack()
            debugPrint("加载时出错", fromName="BotLoopEvent")
            self.exit()
        debugPrint("LoopEvent加载完成", fromName="BotLoopEvent")
        thread = threading.Thread(target=self.kafkaThread)
        thread.start()

    def kafkaThread(self):
        try:
            c = Consumer({
                'bootstrap.servers': 'localhost:9092',
                'group.id': "LoopEventGroup"
            })
            c.subscribe(['BotLoopEvent'])
            self.addToExit(c.close)
            while True:
                msg = c.poll(1.0)
                if msg is not None and not msg.error():
                    msg = loads(msg.value())
                    if "code" not in msg:
                        debugPrint("MSG缺少code", fromName="BotService")
                    else:
                        if msg["code"] == 1:
                            self.exit()
        except Exception:
            printTraceBack()
            self.exit()

    def run(self):
        self.asyncLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.asyncLoop)
        asyncio.run_coroutine_threadsafe(self.loop(), self.asyncLoop)
        self.asyncLoop.run_forever()
