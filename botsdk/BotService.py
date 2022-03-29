import asyncio
import uuid

import botsdk.BotModule.Bot
import botsdk.BotModule.Request
import botsdk.BotRoute
from botsdk.util.BotConcurrentModule import defaultBotConcurrentModule
from botsdk.util.BotPluginsManager import BotPluginsManager
from botsdk.util.Error import debugPrint
from botsdk.util.JsonConfig import getConfig
from botsdk.util.Tool import getAttrFromModule
from botsdk.util.Timer import Timer
from botsdk.util.Error import asyncTraceBack


class BotService:
    def __init__(self):
        self.timer = Timer()

    def getTimer(self):
        return self.timer

    @asyncTraceBack
    async def runInEventLoop(self, accountMark, concurrentModule):
        while True:
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
                        f'''{botName}登陆失败 已重试{loginRetry}次''',
                        fromName="BotService")
                else:
                    break
            debugPrint(f'''账号{botName}登陆成功''', fromName="BotService")
            # 初始化BotRoute
            botRoute = botsdk.BotRoute.BotRoute(
                bot, BotPluginsManager(bot), concurrentModule)
            while True:
                retrySize = 0
                while True:
                    try:
                        if (re := await bot.fetchMessage()) and re[0] == 0:
                            break
                    except Exception:
                        pass
                    retrySize += 1
                    debugPrint(
                        f'''账号{botName}获取消息失败重试:{retrySize + 1}''',
                        fromName="BotService")
                    if retrySize >= 5:
                        loginRetry = 0
                        while True:
                            try:
                                # TypeError: 'int' object is not subscriptable
                                ret = await bot.login()
                            except Exception:
                                ret = 1
                            if ret != 0:
                                debugPrint(
                                    f'''{botName}重登陆失败 已重试{loginRetry}次''',
                                    fromName="BotService")
                            else:
                                break
                            loginRetry += 1
                            await asyncio.sleep(min(loginRetry * 5, 15))
                        debugPrint(
                            f'''账号{botName}重登陆成功''',
                            fromName="BotService")
                        break
                    await asyncio.sleep(min(retrySize * 5, 15))
                for i in ret[1]:
                    request = getAttrFromModule(
                                botPath + ".Request",
                                botType + "Request")(
                                {"bot": bot.getData(),
                                    "uuid": uuid.uuid4()},
                                i, botRoute)
                    if ((canRoute := await bot.filter(request))
                            or canRoute is None):
                        asyncio.run_coroutine_threadsafe(
                            botRoute.route(request), self.loop)
                await asyncio.sleep(
                    bot.getData()[0]["adapterConfig"]["config"]["sleepTime"])

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

    def runInThread(self, func, *args, **kwargs):
        self.concurrentModule.runInThread(func, *args, **kwargs)

    def asyncRunInThread(self, func, *args, **kwargs):
        self.concurrentModule.asyncRunInThread(func, *args, **kwargs)
