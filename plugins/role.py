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
        self.addTarget("GROUP:1", "角色", self.role)
        self.addTarget("GROUP:1", "权限", self.permission)
        self.canDetach = True

    async def role(self, request):
        '''#角色 ADD/DEL ID 角色'''
        data = request.getFirstTextSplit()
        if len(data) < 4:
            await request.sendMessage(self.role.__doc__)
            return
        if ":" in data[3]:
            await request.sendMessage("角色中不许包含:")
            return
        localId = request.getId()
        data[3] = data[3].split(",")
        for i in range(len(data[3])):
            if request.isSingle():
                data[3][i] = request.userFormat(data[3][i])
            else:
                data[3][i] = request.groupFormat(data[3][i])
        cookie = request.getCookie("roles", localId)
        if cookie is None:
            cookie = dict()
        data[2] = request.userFormat(data[2])
        if data[2] not in cookie:
            cookie[data[2]] = []
        if data[1] == "ADD":
            for i in range(len(data[3])):
                if data[3][i] not in cookie[data[2]]:
                    cookie[data[2]].append(data[3][i])
        elif data[1] == "DEL":
            for i in range(len(data[3])):
                if data[3][i] not in cookie[data[2]]:
                    cookie[data[2]].remove(data[3][i])
        else:
            await request.sendMessage("你干啥呢")
            return
        request.setCookie("roles", cookie, localId)
        await request.sendMessage("修改完成")

    async def permission(self, request):
        '''#权限 ADD/DEL 命令 角色'''
        data = request.getFirstTextSplit()
        if len(data) < 4:
            await request.sendMessage(self.permission.__doc__)
            return
        if ":" in data[3]:
            await request.sendMessage("角色中不许包含:")
            return
        localId = request.getId()
        data[3] = data[3].split(",")
        for i in range(len(data[3])):
            if request.isSingle():
                data[3][i] = request.userFormat(data[3][i])
            else:
                data[3][i] = request.groupFormat(data[3][i])
        cookie = request.getCookie("permission", localId)
        if cookie is None:
            cookie = dict()
        childs = request.getId().split(":")[3:]
        for i in childs:
            if f":{i}" not in cookie:
                cookie[f":{i}"] = dict()
            cookie = cookie[f":{i}"]
        if data[2] not in cookie:
            cookie[data[2]] = []
        if data[1] == "ADD":
            for i in range(len(data[3])):
                if data[3][i] not in cookie[data[2]]:
                    cookie[data[2]].append(data[3][i])
        elif data[1] == "DEL":
            for i in range(len(data[3])):
                if data[3][i] not in cookie[data[2]]:
                    cookie[data[2]].remove(data[3][i])
        else:
            await request.sendMessage("你干啥呢")
            return
        request.setCookie("permission", cookie, localId)
        await request.sendMessage("修改完成")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
