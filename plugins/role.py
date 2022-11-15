from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "role"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "角色", self.role)
        self.addTarget("FriendMessage", "角色", self.role)
        self.addTarget("GroupMessage", "权限", self.permission)
        self.addTarget("FriendMessage", "权限", self.permission)
        self.addTarget("GROUP:9", "角色", self.role)
        self.addTarget("GROUP:9", "权限", self.permission)
        self.canDetach = True

    async def role(self, request):
        '''#角色 add/remove ID 角色'''
        data = request.getFirstTextSplit()
        if len(data) != 4:
            await request.sendMessage(self.role.__doc__)
            return
        if ":" in data[3]:
            await request.sendMessage("角色中不许包含:")
            return
        localId = request.getId()
        if request.isSingle():
            localId = request.getBot().getBotName()
        data[2] = data[2].split(",")
        for i in range(len(data[2])):
            data[2][i] = request.userFormat(data[2][i])
        cookie = await request.AsyncGetCookie("roles", localId)
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
        request.setCookie("roles", cookie, localId)
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
        request.setCookie("permission", cookie, localId)
        await request.sendMessage("修改完成")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
