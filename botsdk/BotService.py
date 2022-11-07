import asyncio
import os
import random
import threading
import time
import uuid

from confluent_kafka import Consumer, Producer
from ujson import dumps, loads

from .Module import Module
from .util.Args import GetArgs
from .util.Error import asyncTraceBack, debugPrint, printTraceBack
from .util.JsonConfig import getConfig
from .util.Tool import getAttrFromModule
from .util.ZookeeperTool import AddEphemeralNode, GetZKClient
from threading import Lock


class BotService(Module):
    def init(self):
        self.reProductList = []
        self.reProductListLock = Lock()

    async def BotLogin(self, bot):
        try:
            re = await bot.login()
        except Exception:
            re = 1
        if re != 0:
            return False
        return True

    async def BotLoginLoop(self, bot):
        loginRetrySize = 0
        while True:
            if not await self.BotLogin(bot):
                loginRetrySize += 1
                debugPrint(
                        f'''账号{bot.getBotName()}登陆失败 已重试{loginRetrySize}次''',
                        fromName="BotService")
                await asyncio.sleep(min(1 << loginRetrySize, 16))
            else:
                break
        return loginRetrySize

    def CheckAndGetReproduct(self):
        self.reProductListLock.acquire()
        if len(self.reProductList) == 0:
            ret = []
        else:
            ret = self.reProductList
            self.reProductList = []
        self.reProductListLock.release()
        return ret

    @asyncTraceBack
    async def runInLoop(self, botData):
        while True:
            # 初始化Bot
            botType = botData["botType"]
            botPath = (getConfig()["botPath"] + botType).replace("/", ".")
            botName = botData["botName"]
            debugPrint(f'''账号{botName}加载成功''', fromName="BotService")
            bot = getAttrFromModule(
                botPath + ".Bot",
                botType + "Bot")(botData)
            debugPrint(f'''账号{botName}初始化成功''', fromName="BotService")

            # 登录
            await self.BotLoginLoop(bot)
            debugPrint(f'''账号{botName}登陆成功''', fromName="BotService")

            # 初始化kafka 1.0 update
            self.p = Producer({'bootstrap.servers': 'localhost:9092'})

            # 将Service信息同步至Zookeeper
            if not AddEphemeralNode("/BotProcess", f"{os.getpid()}", {
                            "type": "BotService",
                            "startTime": str(int(time.time())),
                            "botType": botType,
                            "botName": botName
                        }):
                debugPrint(
                        '''BotService同步至zookeeper失败''',
                        fromName="BotService")
                return
            debugPrint('''BotService同步至zookeeper成功''', fromName="BotService")

            # 同步至zookeeper
            if not AddEphemeralNode("/Bot", botName, {
                            "name": botName,
                            "startTime": str(int(time.time())),
                            "data": bot.getData()
                        }):
                debugPrint(
                        f'''账号{botName}同步至zookeeper失败''',
                        fromName="BotService")
                return
            self.addToExit(GetZKClient().stop)
            debugPrint(
                        f'''账号{botName}同步至zookeeper成功''',
                        fromName="BotService")

            # 启动kafka监听线程
            t = threading.Thread(target=self.kafkaThread, args=(botName,))
            t.start()
            '''
            1.0 update
            # 初始化BotRoute
            botRoute = BotRoute(
                bot, BotPluginsManager(bot), self, concurrentModule)
            '''
            # eventLoop
            while True:
                retrySize = 0
                # fetchMessageLoop
                while True:
                    # bot获取消息
                    try:
                        if (ret := await bot.fetchMessage()) and ret[0] == 0:
                            rep = self.CheckAndGetReproduct()
                            if ret[1] or rep:
                                break
                            else:
                                await asyncio.sleep(
                                    bot.getData()[0]
                                    ["adapterConfig"]["config"]["sleepTime"])
                                continue
                    except Exception:
                        pass
                    # 统计出错次数
                    retrySize += 1
                    # 出错五次开始重连
                    if retrySize >= 5:
                        debugPrint(
                            f'''账号{botName}开始重连''',
                            fromName="BotService")
                        await self.BotLoginLoop(bot)
                    else:
                        debugPrint(
                            f'''账号{botName}获取消息失败重试:{retrySize + 1}次''',
                            fromName="BotService")
                        await asyncio.sleep(
                            random.random() + random.randint(1, 2))
                # to router
                for i in rep:
                    self.p.poll(0)
                    self.p.produce(
                            "routeList",
                            i.encode(),
                            callback=self.deliveryReport)
                for i in ret[1]:
                    # 生成uuid
                    localUuid = str(uuid.uuid4())
                    debugPrint(
                            f"收到消息,uuid为{localUuid}",
                            fromName="BotService")
                    # 初始化request
                    request = getAttrFromModule(
                                botPath + ".Request",
                                botType + "Request")(
                                {
                                    "bot": bot.getData(),
                                    "uuid": localUuid,
                                    "botPath": botPath + ".Request",
                                    "botType": botType + "Request"
                                    },
                                i)
                    # 过滤bot自己发的消息
                    if (await bot.filter(request)):
                        self.p.poll(0)
                        self.p.produce(
                                "routeList",
                                dumps(
                                    {"code": 0, "data": request.getData()}
                                    ).encode("utf8"),
                                callback=self.deliveryReport)
                        debugPrint(
                            f"{localUuid}送至Router",
                            fromName="BotService")
                self.p.flush()
                await asyncio.sleep(0)

    def kafkaThread(self, botName):
        try:
            c = Consumer({
                'bootstrap.servers': 'localhost:9092',
                'group.id': botName
            })
            c.subscribe(['BotService'])
            self.addToExit(c.close)
            while True:
                msg = c.poll(1.0)
                if msg is not None and not msg.error():
                    msg = loads(msg.value())
                    if "code" not in msg:
                        debugPrint("MSG缺少code", fromName="BotService")
                    else:
                        if msg["code"] == 1 and msg["data"] == botName:
                            self.exit()
        except Exception:
            printTraceBack()
            self.exit()

    def deliveryReport(self, err, msg):
        if err is None:
            return
        debugPrint(f"消息发送失败:{err}", fromName="BotService")
        self.reProductListLock.acquire()
        self.reProductList.append(msg.value().decode())
        self.reProductListLock.release()

    async def run(self):
        await self.runInLoop(
                loads(GetArgs()["account"].replace("'", '"'))
                )
