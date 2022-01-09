from botsdk.util.BotPlugin import BotPlugin
from botsdk.BotModule.MessageChain import MessageChain


class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "permission"
        self.addTarget("GroupMessage", "权限", self.quanxian)
        self.addTarget("GroupMessage", "群友权限", self.qunyouquanxian)
        self.permissionSet = {"OWNER", "ADMINISTRATOR", "MEMBER"}
        self.canDetach = True

    async def quanxian(self, request):
        '''#群友权限 命令名 所需权限'''
        data = request.getFirstTextSplit()
        if len(data) < 3:
            await request.sendMessage(MessageChain().text("缺少参数"))
            return
        if data[2] not in self.permissionSet:
            await request.sendMessage(MessageChain().text("权限类型错误"))
            return
        cookie = request.getCookie("groupPermission")
        if cookie is None:
            cookie = dict()
        cookie[data[1]] = data[2]
        request.setCookie("groupPermission", cookie)
        await request.sendMessage(MessageChain().text("修改完成"))

    async def qunyouquanxian(self, request):
        '''#群友权限 群友QQ add/remove 权限名'''
        data = request.getFirstTextSplit()
        try:
            target = str(int(data[1]))
        except Exception:
            await request.sendMessage(MessageChain().text("你这什么QQ啊"))
            return
        if len(data) < 4:
            await request.sendMessage(MessageChain().text("缺少参数"))
            return
        cookie = request.getCookie("groupMemberPermission")
        if cookie is None:
            cookie = {}
        if target not in cookie:
            cookie[target] = []
        if data[2] == "add":
            cookie[target].append(data[3])
        elif data[2] == "remove":
            if data[3] in cookie[target]:
                cookie[target].remove(data[3])
        else:
            await request.sendMessage(MessageChain().text("错误操作"))
            return
        request.setCookie("groupMemberPermission", cookie)
        await request.sendMessage(MessageChain().text("修改完成"))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
