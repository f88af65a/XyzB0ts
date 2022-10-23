import asyncio
import os
import random
import threading
import time
import uuid
from json import dumps, loads

from confluent_kafka import Consumer, Producer

from botsdk.util.Args import GetArgs
from botsdk.util.ZookeeperTool import AddEphemeralNode, GetZKClient

from .util.Error import asyncTraceBack, debugPrint
from .util.JsonConfig import getConfig
from .util.Timer import Timer
from .util.Tool import getAttrFromModule


class BotService:
    def __init__(self):
        self.timer = Timer()

    def getTimer(self):
        return self.timer

    @asyncTraceBack
    async def runInEventLoop(self, botData):
        while True:
            # 初始化Bot
            botType = botData["botType"]
            botPath = (getConfig()["botPath"] + botType).replace("/", ".")
            botName = botData["botName"]
            debugPrint(f'''账号{botName}加载成功''', fromName="BotService")
            bot = getAttrFromModule(
                botPath + ".Bot",
                botType + "Bot")(botData)
            bot.setTimer(self.timer)
            debugPrint(f'''账号{botName}初始化成功''', fromName="BotService")

            # 登录
            loginRetry = 0
            while True:
                try:
                    re = await bot.login()
                except Exception:
                    re = 1
                if re != 0:
                    debugPrint(
                        f'''账号{botName}登陆失败 已重试{loginRetry}次''',
                        fromName="BotService")
                else:
                    break
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
                    try:
                        if (ret := await bot.fetchMessage()) and ret[0] == 0:
                            if not len(ret[1]):
                                await asyncio.sleep(
                                    bot.getData()[0]
                                    ["adapterConfig"]["config"]["sleepTime"])
                                continue
                            else:
                                break
                    except Exception:
                        pass
                    retrySize += 1
                    if retrySize >= 5:
                        loginRetry = 0
                        # reLoginLoop
                        while True:
                            try:
                                ret = await bot.login()
                            except Exception:
                                ret = 1
                            if ret != 0:
                                debugPrint(
                                    f'''账号{botName}重登失败重试:{loginRetry}次''',
                                    fromName="BotService")
                            else:
                                break
                            loginRetry += 1
                            await asyncio.sleep(min(loginRetry * 5, 15))
                        debugPrint(
                            f'''账号{botName}重登陆成功''',
                            fromName="BotService")
                    else:
                        debugPrint(
                            f'''账号{botName}获取消息失败重试:{retrySize + 1}次''',
                            fromName="BotService")
                        await asyncio.sleep(
                            random.random() + random.randint(1, 2))
                # to router
                for i in ret[1]:
                    ''' 1.0 update
                    request = getAttrFromModule(
                                botPath + ".Request",
                                botType + "Request")(
                                {"bot": bot.getData(),
                                    "uuid": uuid.uuid4()},
                                i, botRoute)
                    '''
                    request = getAttrFromModule(
                                botPath + ".Request",
                                botType + "Request")(
                                {
                                    "bot": bot.getData(),
                                    "uuid": str(uuid.uuid4()),
                                    "botPath": botPath + ".Request",
                                    "botType": botType + "Request"
                                    },
                                i)
                    if (await bot.filter(request)):
                        '''
                        1.0 update
                        asyncio.run_coroutine_threadsafe(
                            botRoute.route(request), self.loop)
                        '''
                        self.p.poll(0)
                        self.p.produce(
                                "routeList",
                                dumps(
                                    {"code": 0, "data": request.getData()}
                                    ).encode("utf8"),
                                callback=self.deliveryReport)
                self.p.flush()
                await asyncio.sleep(0)

    def kafkaThread(self, botName):
        self.c = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': botName
        })
        self.c.subscribe(['BotService'])
        while True:
            msg = self.c.poll(1.0)
            if msg is not None and not msg.error():
                msg = loads(msg.value())
                if "code" not in msg:
                    debugPrint("MSG缺少code", fromName="BotService")
                else:
                    if msg["code"] == 1 and msg["data"] == botName:
                        self.c.close()
                        GetZKClient().stop()
                        exit()

    def deliveryReport(self, err, msg):
        if err is not None:
            debugPrint('Message delivery failed: {}'.format(err))
        else:
            debugPrint('Message delivered to {} [{}]'.format(
                    msg.topic(), msg.partition()))

    def run(self):
        '''
        1.0 update
        concurrentModule = defaultBotConcurrentModule(
            int(getConfig()["workProcess"]) if getConfig()["multi"] else None,
            int(getConfig()["workThread"]))
        asyncio.run_coroutine_threadsafe(
            self.runInEventLoop(
                loads(GetArgs()["account"].split("'", '"')), concurrentModule),
            self.loop)
        asyncio.run_coroutine_threadsafe(self.timer.timerLoop(), self.loop)
        '''
        asyncio.run(self.runInEventLoop(
                loads(GetArgs()["account"].replace("'", '"')))
                )
