from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Cookie import AsyncGetCookie, AsyncSetCookie
from botsdk.util.JsonConfig import getConfig


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "permissionPlugin"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "角色", self.role)
        self.addTarget("FriendMessage", "角色", self.role)
        self.addTarget("GroupMessage", "role", self.role)
        self.addTarget("FriendMessage", "role", self.role)
        self.addTarget("GroupMessage", "权限", self.permission)
        self.addTarget("FriendMessage", "权限", self.permission)
        self.addTarget("GroupMessage", "permission", self.permission)
        self.addTarget("FriendMessage", "permission", self.permission)
        self.addTarget("GROUP:9", "角色", self.role)
        self.addTarget("GROUP:9", "权限", self.permission)
        self.addTarget("GROUP:9", "role", self.role)
        self.addTarget("GROUP:9", "permission", self.permission)
        self.addTarget("GroupMessage", "getRole", self.getRole)
        self.addTarget("FriendMessage", "getRole", self.getRole)
        self.addTarget("GROUP:9", "getRole", self.getRole)
        self.addTarget("GroupMessage", "banTarget", self.banTarget)
        self.addTarget("FriendMessage", "banTarget", self.banTarget)
        self.addTarget("GROUP:9", "banTarget", self.banTarget)

    async def role(self, request):
        '''#角色 add/remove ID 角色'''
        data = request.getFirstTextSplit()
        if len(data) != 4:
            await request.sendMessage(self.role.__doc__)
            return
        if ":" in data[3]:
            await request.sendMessage("角色中不许包含:")
            return

        userId = request.userFormat(data[2])
        if request.isSingle():
            data[2] = (
                f"{request.getBot().getBotName()}:"
                f"{request.userFormat(data[2])}"
            )
        else:
            data[2] = request.getId()
        cookie = await AsyncGetCookie(data[2], "roles")
        if cookie is None:
            cookie = dict()
        if userId not in cookie:
            cookie[userId] = []
        if data[1] == "add":
            if data[3] not in cookie[userId]:
                cookie[userId].append(data[3])
        elif data[1] == "remove":
            if data[3] in cookie[userId]:
                cookie[userId].remove(data[3])
        else:
            await request.sendMessage("你干啥呢")
            return
        await AsyncSetCookie(data[2], "roles", cookie)
        await request.sendMessage("修改完成")

    async def permission(self, request):
        '''#权限 add/remove 命令 角色'''
        data = request.getFirstTextSplit()
        if len(data) != 4:
            await request.sendMessage(self.permission.__doc__)
            return
        if ":" in data[3]:
            await request.sendMessage("角色中不许包含:")
            return
        localId = request.getId()
        if request.isSingle():
            localId = request.getBot().getBotName()
        cookie = await request.AsyncGetCookie("permission", localId)
        if cookie is None:
            cookie = dict()
        if data[2] not in cookie:
            cookie[data[2]] = []
        if data[1] == "add":
            if data[3] not in cookie[data[2]]:
                cookie[data[2]].append(data[3])
        elif data[1] == "remove":
            if data[3] in cookie[data[2]]:
                cookie[data[2]].remove(data[3])
        else:
            await request.sendMessage("你干啥呢")
            return
        await request.AsyncSetCookie("permission", cookie, localId)
        await request.sendMessage("修改完成")

    async def getRole(self, request):
        ret = await request.getRoles()
        userId = request.getUserId()
        if userId is None:
            return False
        systemCookie = getConfig()["systemCookie"]
        if userId in systemCookie["user"]:
            ret |= set(systemCookie["user"][userId])
        cookie = await request.AsyncGetCookie("roles")
        if cookie and userId in cookie:
            ret |= set(cookie[userId])
        await request.send(str(ret))

    async def banTarget(self, request):
        '''banTarget add/remove 命令 ID'''
        commandList = ["add", "remove"]
        data = request.getFirstTextSplit()
        if len(data) != 4 or data[1] not in commandList:
            await request.send(self.banTarget.__doc__)
            return
        cookie = await AsyncGetCookie(
            request.getBot().getBotName(),
            "BanTarget"
        )
        if cookie is None:
            cookie = {}
        if data[3] not in cookie:
            cookie[data[3]] = []
        if data[1] == "add":
            if data[2] not in cookie[data[3]]:
                cookie[data[3]].append(data[2])
        elif data[1] == "remove":
            if data[2] in cookie[data[3]]:
                cookie[data[3]].remove(data[2])
        await AsyncSetCookie(
            request.getBot().getBotName(),
            "BanTarget",
            cookie
        )
        await request.send("修改完成")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
