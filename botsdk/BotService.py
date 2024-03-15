import asyncio
import os
import random
import time
import uuid

from ujson import dumps, loads

from .Module import Module
from .util.Args import GetArgs
from .util.Error import asyncTraceBack, debugPrint, printTraceBack
from .util.JsonConfig import getConfig
from .util.Tool import getAttrFromModule


class BotService(Module):
    def init(self):
        pass

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

    async def SyncToKeeper(self, bot):
        botPath = f"/Bot/{bot.getBotName()}"
        botData = {
                "name": bot.getBotName(),
                "startTime": str(int(time.time())),
                "data": bot.getData()
            }
        await self.keeper.Set(
            botPath,
            botData
        )

    @asyncTraceBack
    async def runInLoop(self, botData):
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

        # 同步至zookeeper
        await self.SyncToKeeper(bot)
        debugPrint(
            f'''账号{botName}同步至zookeeper成功''',
            fromName="BotService"
        )

        # 将Service信息同步至Zookeeper
        await self.keeper.Set(
            f"/BotProcess/{os.getpid()}",
            {
                "type": "BotService",
                "startTime": str(int(time.time())),
                "botType": botType,
                "botName": botName
             }
        )
        debugPrint('''BotService同步至keeper成功''', fromName="BotService")

        # eventLoop
        while True:
            retrySize = 0
            # fetchMessageLoop
            while True:
                # bot获取消息
                try:
                    if (ret := await bot.fetchMessage()) and ret[0] == 0:
                        if ret[1]:
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
                    debugPrint(
                        f'''账号{botName}重连成功''',
                        fromName="BotService")
                    if not self.SyncToKeeper(bot):
                        debugPrint(
                            f'''账号{botName}同步失败''',
                            fromName="BotService")
                        self.exit()
                    debugPrint(
                        f'''账号{botName}同步成功''',
                        fromName="BotService")
                else:
                    debugPrint(
                        f'''账号{botName}获取消息失败重试:{retrySize + 1}次''',
                        fromName="BotService")
                    await asyncio.sleep(
                        random.random() + random.randint(1, 2))

            # to router
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
                            "botType": botType + "Request",
                            "recvTime": int(time.time())
                        },
                        i
                    )

                # 过滤bot自己发的消息
                if (await bot.filter(request)):
                    await self.sendMessage(
                        "RouteQueue",
                        dumps(
                            {
                                "code": 0,
                                "data": request.getData()
                            }
                        ).encode()
                    )
                    debugPrint(
                        f"{localUuid}送至Router",
                        fromName="BotService"
                    )
            await asyncio.sleep(0)

    async def run(self):
        await self.runInLoop(
            self.extend["account"]
        )
