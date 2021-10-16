from botsdk.tool.JsonConfig import *
import asyncio
import botsdk.Bot
import botsdk.BotRequest
import botsdk.BotRoute
from botsdk.tool.Error import *
from botsdk.tool.BotConcurrentModule import defaultBotConcurrentModule

class BotService:
    def __init__(self):
        pass

    async def runInEventLoop(self):
        #初始化Bot
        self.bot = botsdk.Bot.Bot(getConfig()["api"]["path"], getConfig()["api"]["port"])
        #登录
        re = await self.bot.login(getConfig()["account"]["qq"], getConfig()["account"]["passwd"])
        if re != 0:
            exceptionExit("BotService", "登录出错")
        #初始化BotRoute
        self.botRoute = botsdk.BotRoute.BotRoute( self.bot, \
            defaultBotConcurrentModule(int(getConfig()["workProcess"]) \
            if getConfig()["multi"] else None, int(getConfig()["workThread"])))
        self.botRoute.init()
        while True:
            re = await self.bot.fetchMessage(128)
            _readList = []
            if "data" not in re or len(re["data"]) == 0:
                await asyncio.sleep(0.05)
                continue
            for i in range(0,len(re["data"])):
                _readList.append(re["data"][i])
            for i in re["data"]:
                asyncio.run_coroutine_threadsafe( \
                    self.botRoute.route(botsdk.BotRequest.BotRequest( \
                        i, self.bot, self.botRoute)) \
                    ,self.loop)

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.runInEventLoop())
