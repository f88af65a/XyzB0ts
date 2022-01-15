from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "role"
        self.addTarget("GroupMessage", "角色", self.role)
        self.addTarget("GroupMessage", "权限", self.permission)
        self.addTarget("GROUP:1", "角色", self.role)
        self.addTarget("GROUP:1", "权限", self.permission)
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.canDetach = True

    async def role(self, request):
        '''#角色 ADD/DEL ID 角色'''
        data = request.getFirstTextSplit()
        if len(data) < 4:
            await request.sendMessage("缺少参数")
            return
        if ":" in data[3]:
            await request.sendMessage("角色中不许包含:")
            return
        cookie = request.getCookie("roles")
        if cookie is None:
            cookie = dict()
        data[2] = f"""{request.getBot().getBotType()}:User:{data[2]}"""
        if data[2] not in cookie:
            cookie[data[2]] = []
        if data[1] == "ADD":
            if data[3] not in cookie[data[2]]:
                cookie[data[2]].append(data[3])
        elif data[1] == "DEL":
            if data[3] in cookie[data[2]]:
                cookie[data[2]].remove(data[3])
        else:
            await request.sendMessage("你干啥呢")
            return
        request.setCookie("roles", cookie)
        await request.sendMessage("修改完成")

    async def permission(self, request):
        '''#权限 ADD/DEL 命令 角色'''
        data = request.getFirstTextSplit()
        if len(data) < 4:
            await request.sendMessage("缺少参数")
            return
        if ":" in data[3]:
            await request.sendMessage("角色中不许包含:")
            return
        cookie = request.getCookie("permission")
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
            if data[3] not in cookie[data[2]]:
                cookie[data[2]].append(data[3])
        elif data[1] == "DEL":
            if data[3] in cookie[data[2]]:
                cookie[data[2]].remove(data[3])
        else:
            await request.sendMessage("你干啥呢")
            return
        request.setCookie("permission", cookie)
        await request.sendMessage("修改完成")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
