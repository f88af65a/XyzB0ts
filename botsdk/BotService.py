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


class BotService:
    def __init__(self):
        pass

    async def runInEventLoop(self, accountMark, concurrentModule):
        while True:
            botPath = (getConfig()["botPath"]
                       + getConfig()["account"][accountMark]["botType"])
            # 初始化Bot
            botName = getConfig()["account"][accountMark]["botName"]
            bot = getAttrFromModule(
                botPath + "Bot",
                botName + "Bot")(getConfig()["account"][accountMark])
            # 登录
            re = bot.login()
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
                    if (re := await bot.fetchMessage()) is not None:
                        break
                    else:
                        retrySize += 1
                        debugPrint(
                            f'''账号{botName}获取消息失败重试:{retrySize + 1}''',
                            fromName="BotService")
                        await bot.onError(re)
                        await asyncio.sleep(retrySize * 5)
                for i in re:
                    asyncio.run_coroutine_threadsafe(
                        botRoute.route(
                            getAttrFromModule(
                                botPath + "Request",
                                botName + "Request")(
                                {"bot": bot.getData(),
                                    "uuid": uuid.uuid4()},
                                i, botRoute)),
                        self.loop
                        )

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
        self.loop.run_forever()
