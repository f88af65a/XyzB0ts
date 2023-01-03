import asyncio
import copy

from botsdk.util.BotNotifyModule import AsyncGetNotifyList
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.ZookeeperTool import GetBotByName
from botsdk.util.Cache import GetCacheInstance
from botsdk.util.Permission import permissionCheck


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "FunctionalTest"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "setCache", self.setCache)
        self.addTarget("GROUP:9", "setCache", self.setCache)
        self.addTarget("GroupMessage", "getCache", self.getCache)
        self.addTarget("GROUP:9", "getCache", self.getCache)
        self.addTarget("GroupMessage", "permission", self.permissionCheckTest)
        self.addTarget("GROUP:9", "permission", self.permissionCheckTest)

    def init(self):
        self.addLoopEvent(self.notifyTest)

    async def setCache(self, request):
        "setCache key val ex #设置cache"
        data = request.getFirstTextSplit()
        if len(data) != 4:
            await request.send(self.setCache.__doc__)
            return
        try:
            data[3] = int(data[3])
        except Exception:
            await request.send("EX应为数字")
            return
        await GetCacheInstance().SetCache(data[1], data[2], data[3])
        await request.send("设置成功")

    async def getCache(self, request):
        "getCache key #获取cache"
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.getCache.__doc__)
            return
        await request.send(
            str(await GetCacheInstance().GetCache(data[1]))
        )

    async def notifyTest(self):
        while True:
            await asyncio.sleep(10)
            notifySet = copy.deepcopy(
                    await AsyncGetNotifyList("bot.notify.test"))
            for i in notifySet:
                botName = i.split(":")[0]
                bot = GetBotByName(botName)
                if bot is None:
                    continue
                dynamicChain = bot.makeMessageChain().text("hello")
                await bot.sendMessage(dynamicChain, id=i)

    async def permissionCheckTest(self, request):
        "permission target #测试权限"
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.permissionCheckTest.__doc__)
            return
        if permissionCheck(request, data[1]):
            await request.send("拥有权限")
        else:
            await request.send("没有权限")


def handle():
    return plugin()
