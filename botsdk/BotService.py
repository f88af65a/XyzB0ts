import uuid
import asyncio
import botsdk.Bot
import botsdk.BotRequest
import botsdk.BotRoute
from botsdk.tool.JsonConfig import *
from botsdk.tool.Error import *
from botsdk.tool.BotConcurrentModule import defaultBotConcurrentModule

class BotService:
    def __init__(self):
        pass

    async def runInEventLoop(self, accountMark, concurrentModule):
        while True:
            #初始化信息
            qq = getConfig()["account"][accountMark]["qq"]
            #初始化Bot
            self.bot = botsdk.Bot.Bot(getConfig()["account"][accountMark]["path"]
                , getConfig()["account"][accountMark]["port"])
            #登录
            re = await self.bot.login(qq
                , getConfig()["account"][accountMark]["passwd"])
            if re != 0:
                debugPrint(f'''账号{qq}登陆失败''', fromName="BotService")
                return
            debugPrint(f'''账号{qq}登陆成功''', fromName="BotService")
            #初始化BotRoute
            self.botRoute = botsdk.BotRoute.BotRoute(self.bot, concurrentModule)
            self.botRoute.init()
            while True:
                retrySize = 0
                while True:
                    try:
                        re = await self.bot.fetchMessage(128)
                        break
                    except Exception as e:
                        retrySize += 1
                        debugPrint(f'''账号{qq}获取消息失败重试:{retrySize + 1}'''
                            , fromName="BotService")
                        await asyncio.sleep(retrySize * 5)
                if re["data"] != 0:
                    debugPrint(f'账号{qq}返回了一个错误的code:{re["code"]} {re["msg"]}')
                    break
                _readList = []
                if "data" not in re or len(re["data"]) == 0:
                    await asyncio.sleep(0.05)
                    continue
                for i in range(0,len(re["data"])):
                    _readList.append(re["data"][i])
                for i in re["data"]:
                    asyncio.run_coroutine_threadsafe( \
                        self.botRoute.route(botsdk.BotRequest.BotRequest( \
                            {"bot":self.bot.getData(),"uuid":uuid.uuid4()}, i, self.botRoute)) \
                        ,self.loop)

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        concurrentModule = defaultBotConcurrentModule(int(getConfig()["workProcess"]) \
            if getConfig()["multi"] else None, int(getConfig()["workThread"]))
        for i in range(len(getConfig()["account"])):
            asyncio.run_coroutine_threadsafe(self.runInEventLoop(i, concurrentModule), self.loop)
        self.loop.run_forever()
