import asyncio
import importlib
import json
import os
import time

from confluent_kafka import Consumer

from botsdk.util.HandlePacket import asyncHandlePacket
from botsdk.util.ZookeeperTool import AddEphemeralNode

from .util.Error import debugPrint, printTraceBack
from .util.Tool import getAttrFromModule


class BotHandle:
    def __init__(self):
        pass

    async def Loop(self):
        # 将Handle信息同步至Zookeeper
        if not AddEphemeralNode("/BotProcess", f"{os.getpid()}", {
                        "type": "BotHandle",
                        "startTime": str(int(time.time()))
                    }):
            debugPrint(
                    '''BotHandle同步至zookeeper失败''',
                    fromName="BotRouter")
        debugPrint('''BotHandle同步至zookeeper成功''', fromName="BotHandle")
        c = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': "targetHandleGroup"
        })
        c.subscribe(['targetHandle'])
        while True:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                debugPrint(msg.error())
                continue
            msg = json.loads(msg.value())
            try:
                module = importlib.reload(importlib.import_module(msg["path"]))
                plugin = getattr(module, "handle")()
                plugin.onLoad()
                if not plugin.initBySystem():
                    debugPrint(
                            f'''{msg["path"]}.{msg["handle"]}初始化失败''',
                            fromName="BotHandle")
                    continue
                handle = getattr(plugin, msg["handle"])
            except Exception:
                printTraceBack()
                return
            request = msg["request"]
            request = getAttrFromModule(
                    request[0]["botPath"],
                    request[0]["botType"]
                )(request[0], request[1])
            try:
                await asyncHandlePacket(handle, request)
            except Exception:
                printTraceBack()

    def run(self):
        asyncio.run(self.Loop())
