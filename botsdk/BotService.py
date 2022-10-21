import asyncio
import random
import uuid
from json import dumps

from confluent_kafka import Producer
from kazoo.client import KazooClient

from .util.BotConcurrentModule import defaultBotConcurrentModule
from .util.Error import asyncTraceBack, debugPrint, printTraceBack
from .util.JsonConfig import getConfig
from .util.Timer import Timer
from .util.Tool import getAttrFromModule


class BotService:
    def __init__(self):
        self.timer = Timer()

    def getTimer(self):
        return self.timer

    @asyncTraceBack
    async def runInEventLoop(self, accountMark, concurrentModule):
        while True:
            # 初始化kafka 1.0 update
            self.p = Producer({'bootstrap.servers': 'localhost:9092'})

            # 初始化Bot
            botType = getConfig()["account"][accountMark]["botType"]
            botPath = (getConfig()["botPath"] + botType).replace("/", ".")
            botName = getConfig()["account"][accountMark]["botName"]
            debugPrint(f'''账号{botName}加载成功''', fromName="BotService")
            bot = getAttrFromModule(
                botPath + ".Bot",
                botType + "Bot")(getConfig()["account"][accountMark])
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

            # 同步至zookeeper
            try:
                zk = KazooClient(hosts="127.0.0.1:2181")
                zk.start()
                try:
                    if not zk.exists("/bot"):
                        zk.create("/bot")
                except Exception:
                    printTraceBack()
                zk.create(
                        f"/bot/{botName}",
                        dumps({
                            "name": botName,
                            "data": dumps(bot.getData())
                        }).encode(),
                        ephemeral=True
                    )
            except Exception:
                printTraceBack()
                return
            debugPrint(f'''账号{botName}同步至zookeeper成功''', fromName="BotService")
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
                                dumps(request.getData()).encode("utf8"),
                                callback=self.deliveryReport)
                self.p.flush()
                await asyncio.sleep(0)

    def deliveryReport(self, err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(
                    msg.topic(), msg.partition()))

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        concurrentModule = defaultBotConcurrentModule(
            int(getConfig()["workProcess"]) if getConfig()["multi"] else None,
            int(getConfig()["workThread"]))
        for i in range(len(getConfig()["account"])):
            asyncio.run_coroutine_threadsafe(
                self.runInEventLoop(i, concurrentModule),
                self.loop)
        asyncio.run_coroutine_threadsafe(self.timer.timerLoop(), self.loop)
        self.loop.run_forever()
