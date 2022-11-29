from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Cookie import AsyncGetCookie, AsyncSetCookie


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "role"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "角色", self.grouprole)
        self.addTarget("FriendMessage", "角色", self.friendrole)
        self.addTarget("GroupMessage", "role", self.grouprole)
        self.addTarget("FriendMessage", "role", self.friendrole)
        self.addTarget("GroupMessage", "权限", self.permission)
        self.addTarget("FriendMessage", "权限", self.permission)
        self.addTarget("GroupMessage", "permission", self.permission)
        self.addTarget("FriendMessage", "permission", self.permission)
        self.addTarget("GROUP:9", "角色", self.grouprole)
        self.addTarget("GROUP:9", "权限", self.permission)
        self.addTarget("GROUP:9", "role", self.grouprole)
        self.addTarget("GROUP:9", "permission", self.permission)

    async def grouprole(self, request):
        '''#角色 add/remove ID 角色'''
        data = request.getFirstTextSplit()
        if len(data) != 4:
            await request.sendMessage(self.role.__doc__)
            return
        if ":" in data[3]:
            await request.sendMessage("角色中不许包含:")
            return
        data[2] = data[2].split(",")
        for i in range(len(data[2])):
            data[2][i] = request.userFormat(data[2][i])
        cookie = await request.AsyncGetCookie("roles")
        if cookie is None:
            cookie = dict()
        for i in range(len(data[2])):
            if data[2][i] not in cookie:
                cookie[data[2][i]] = []
        if data[1] == "add":
            for i in range(len(data[2])):
                if data[3] not in cookie[data[2][i]]:
                    cookie[data[2][i]].append(data[3])
        elif data[1] == "remove":
            for i in range(len(data[2])):
                if data[3] in cookie[data[2][i]]:
                    cookie[data[2][i]].remove(data[3])
        else:
            await request.sendMessage("你干啥呢")
            return
        await request.AsyncSetCookie("roles", cookie)
        await request.sendMessage("修改完成")

    async def friendrole(self, request):
        '''#角色 add/remove ID 角色'''
        data = request.getFirstTextSplit()
        if len(data) != 4:
            await request.sendMessage(self.role.__doc__)
            return
        if ":" in data[3]:
            await request.sendMessage("角色中不许包含:")
            return
        data[2] = (
            f"{request.getBot().getBotName()}:{request.userFormat(data[2])}"
        )
        cookie = await AsyncGetCookie(data[2], "roles")
        if cookie is None:
            cookie = dict()
        if data[2] not in cookie:
            cookie[data[2]] = []
        if data[1] == "add":
            cookie[request.userFormat(data[2])].append(data[3])
        elif data[1] == "remove":
            if data[3] in cookie[data[2]]:
                cookie[request.userFormat(data[2])].remove(data[3])
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


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
