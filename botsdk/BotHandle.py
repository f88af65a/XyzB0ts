import asyncio
import importlib
import os
import time
from ujson import loads
import threading
from confluent_kafka import Consumer

from .Module import Module
from .util.Error import debugPrint, printTraceBack
from .util.HandlePacket import asyncHandlePacket
from .util.Tool import getAttrFromModule
from .util.ZookeeperTool import AddEphemeralNode, GetZKClient


class BotHandle(Module):
    async def runInLoop(self):
        # 将Handle信息同步至Zookeeper
        if not AddEphemeralNode("/BotProcess", f"{os.getpid()}", {
                        "type": "BotHandle",
                        "startTime": str(int(time.time()))
                    }):
            debugPrint(
                    '''BotHandle同步至zookeeper失败''',
                    fromName="BotRouter")
        self.addToExit(GetZKClient().stop)
        debugPrint('''BotHandle同步至zookeeper成功''', fromName="BotHandle")
        fetchMessageThread = threading.Thread(target=self.fetchMessageThread)
        fetchMessageThread.start()

    def fetchMessageThread(self):
        debugPrint('''消息获取线程启动''', fromName="BotHandle")
        c = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': "targetHandleGroup"
        })
        c.subscribe(['targetHandle'])
        self.addToExit(c.close)
        while True:
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
            debugPrint(f"成功收到消息:{request.getUuid()}", fromName="BotHandle")
            asyncio.run_coroutine_threadsafe(
                    self.DoInEventLoop(
                        handle,
                        request
                    ),
                    self.loop
                )

    async def DoInEventLoop(self, handle, request):
        try:
            await asyncHandlePacket(handle, request)
        except Exception as e:
            await request.send(str(e))
            printTraceBack()

    async def run(self):
        await self.runInLoop()
