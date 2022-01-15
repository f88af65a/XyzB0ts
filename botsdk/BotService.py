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
            debugPrint(f'''账号{botName}初始化成功''', fromName="BotService")
            # 登录
            re = await bot.login()
            if re != 0:
                debugPrint(f'''{botName}登陆失败''', fromName="BotService")
                return
            debugPrint(f'''账号{botName}登陆成功''', fromName="BotService")
            # 初始化BotRoute
            botRoute = botsdk.BotRoute.BotRoute(
                bot, BotPluginsManager(bot), concurrentModule)
            while True:
                retrySize = 0
                while True:
                    if (re := await bot.fetchMessage()) and re[0] == 0:
                        break
                    else:
                        retrySize += 1
                        debugPrint(
                            f'''账号{botName}获取消息失败重试:{retrySize + 1}''',
                            fromName="BotService")
                        await asyncio.sleep(retrySize * 5)
                for i in re[1]:
                    asyncio.run_coroutine_threadsafe(
                        botRoute.route(
                            getAttrFromModule(
                                botPath + ".Request",
                                botType + "Request")(
                                {"bot": bot.getData(),
                                    "uuid": uuid.uuid4()},
                                i, botRoute)),
                        self.loop
                        )
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
