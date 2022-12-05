import asyncio
import os
import threading
import time

from confluent_kafka import Consumer
from ujson import loads

from .Module import Module
from .util.BotPluginsManager import BotPluginsManager
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
        pluginsManager = BotPluginsManager()
        debugPrint('''插件初始化完成''', fromName="BotHandle")
        while True:
            # 获取msg
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                debugPrint(msg.error())
                continue

            # 初始化msg
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

            # 初始化request
            request = msg["request"]
            request = getAttrFromModule(
                    request[0]["botPath"],
                    request[0]["botType"]
                )(request[0], request[1])
            debugPrint(f"收到消息:{request.getUuid()}", fromName="BotHandle")
            if time.time() - request.getRecvTime() >= 60:
                debugPrint(
                    (
                        f"消息{request.getUuid()}超时 当前时间:"
                        f'''{time.strftime(
                            "%H:%M:%S", time.localtime()
                            )} '''
                        f'''接受时间:{time.strftime(
                            "%H:%M:%S", time.localtime(
                                request.getRecvTime()
                                )
                            )}'''
                    ),
                    fromName="BotHandle"
                )
                continue
            # 获取Handle
            try:
                handles = self.GetHandleByMessage(
                        pluginsManager, msg, request
                )
                if not handles:
                    debugPrint(
                        f"消息:{request.getUuid()}获取Handle失败",
                        fromName="BotHandle"
                    )
                    continue
            except Exception:
                printTraceBack()
                continue
            # 调用handle
            debugPrint(f"成功收到消息:{request.getUuid()}", fromName="BotHandle")
            request.setPluginManager(pluginsManager)
            for i in handles:
                asyncio.run_coroutine_threadsafe(
                        self.DoInEventLoop(
                            i,
                            request
                        ),
                        self.loop
                    )
        debugPrint(
            "BotHandle意外结束",
            fromName="BotHandle"
        )

    def GetHandleByMessage(self, pluginsManager, msg, request):
        if msg["msgType"] == 0:
            ret = pluginsManager.getHandleByType(
                msg["type"]
            )
            if not ret:
                debugPrint(
                        f'''{msg["type"]}缺少Handle''',
                        fromName="BotHandle"
                    )
                return None
            return list(ret)
        elif msg["msgType"] == 1:
            return [pluginsManager.getHandleByTarget(
                request.getType(),
                msg["target"]
            )]

    async def DoInEventLoop(self, handle, request):
        try:
            await asyncHandlePacket(handle, request)
        except Exception as e:
            await request.send(str(e))
            printTraceBack()

    async def run(self):
        await self.runInLoop()
