import asyncio
import copy

from botsdk.util.BotNotifyModule import AsyncGetNotifyList
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.ZookeeperTool import GetBotByName
from botsdk.util.Cache import GetCacheInstance
from botsdk.util.Permission import permissionCheck
from botsdk.util.Cookie import GetAsyncCookieDriver


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "FunctionalTest"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "setCache", self.setCache)
        self.addTarget("GROUP:9", "setCache", self.setCache)
        self.addTarget("GroupMessage", "getCache", self.getCache)
        self.addTarget("GROUP:9", "getCache", self.getCache)
        self.addTarget(
            "GroupMessage", "permissionCheck", self.permissionCheckTest
        )
        self.addTarget(
            "FriendMessage", "permissionCheck", self.permissionCheckTest
        )
        self.addTarget(
            "GROUP:9", "permissionCheck", self.permissionCheckTest
        )
        self.addTarget(
            "GroupMessage", "searchCookie", self.searchCookie
        )
        self.addTarget(
            "FriendMessage", "searchCookie", self.searchCookie
        )
        self.addTarget(
            "GROUP:9", "searchCookie", self.searchCookie
        )
        self.addTarget(
            "GROUP:9", "创建分组", self.createCategory
        )
        self.addTarget(
            "GROUP:9", "创建角色", self.createRole
        )
        self.addTarget(
            "GROUP:9", "查看频道角色", self.getChannelRole
        )
        self.addTarget(
            "GROUP:9", "创建频道角色", self.createChannelRole
        )
        self.addTarget(
            "GROUP:9", "更新频道角色", self.updateChannelRole
        )
        self.addTarget(
            "GROUP:9", "更新角色", self.updateRole
        )

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
        "permissionCheck target #测试权限"
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.permissionCheckTest.__doc__)
            return
        if permissionCheck(request, data[1]):
            await request.send("拥有权限")
        else:
            await request.send("没有权限")

    async def searchCookie(self, request):
        "searchCookie key #搜索cookie"
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.searchCookie.__doc__)
            return
        ret = await ((await GetAsyncCookieDriver()).AsyncFindCookie(data[1]))
        await request.send(str(ret))

    async def createCategory(self, request):
        "创建分组 分组名 #创建一个分组"
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.createCategory.__doc__)
            return
        await (request.getBot().createChannel(
            request["extra"]["guild_id"],
            "",
            data[1],
            0,
            0,
            "",
            1
        ))
        await request.send("OK")

    async def createRole(self, request):
        "创建分组 分组名 #创建一个分组"
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.createCategory.__doc__)
            return
        ret = await (request.getBot().createRole(
            request["extra"]["guild_id"],
            data[1]
        ))
        await request.send(str(ret))

    async def getChannelRole(self, request):
        "查看频道角色 频道id #查看频道角色列表"
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.getChannelRole.__doc__)
            return
        ret = await (request.getBot().getChannelRole(
            data[1]
        ))
        await request.send(str(ret))

    async def createChannelRole(self, request):
        "创建频道角色 频道id 类型 角色id #创建频道角色"
        data = request.getFirstTextSplit()
        if len(data) != 4:
            await request.send(self.createChannelRole.__doc__)
            return
        if data[2] not in ["role_id", "user_id"]:
            await request.send(self.createChannelRole.__doc__)
            return
        ret = await (request.getBot().createChannelRole(
            data[1],
            data[2],
            data[3]
        ))
        await request.send(str(ret))

    async def updateChannelRole(self, request):
        "更新频道角色 频道id 类型 id allow deny #更新频道角色"
        data = request.getFirstTextSplit()
        if len(data) != 6:
            await request.send(self.updateChannelRole.__doc__)
            return
        ret = await (request.getBot().updateChannelRole(
            data[1],
            data[2],
            data[3],
            int(data[4]),
            int(data[5])
        ))
        await request.send(str(ret))

    async def updateRole(self, request):
        "更新角色 服务器 角色id 颜色 #更新角色"
        data = request.getFirstTextSplit()
        if len(data) != 4:
            await request.send(self.updateRole.__doc__)
            return
        ret = await (request.getBot().updateRole(
            data[1],
            data[2],
            color=int(data[3])
        ))
        await request.send(str(ret))


def handle():
    return plugin()
