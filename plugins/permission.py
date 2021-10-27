import botsdk.BotRequest
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.Cookie import *

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.listenType = []
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenTarget = [["GroupMessage", "权限", self.quanxian], \
                             ["GroupMessage", "群友权限", self.qunyouquanxian] \
                             ]
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.name = "permission"
        #"插件名称"
        self.info = "权限管理"
        #"插件信息"
        self.help = "/权限 命令 [OWNER/ADMINISTRATOR/MEMBER]\n/群友权限 群友qq [add/remove] 命令"
        #"插件帮助"
        self.permissionSet = {"OWNER","ADMINISTRATOR","MEMBER"}

    async def quanxian(self, request):
        data = request.getFirstTextSplit()
        groupid = request.getGroupId()
        if len(data) < 3:
            await request.sendMessage(MessageChain().text("缺少参数"))
            return
        if data[2] not in self.permissionSet:
            await request.sendMessage(MessageChain().text("权限类型错误"))
            return
        cookie = getCookieByDict(groupid)
        if "groupPermission" not in cookie:
            cookie["groupPermission"] = {}
        cookie["groupPermission"][data[1]] = data[2]
        setCookieByDict(groupid, cookie)
        await request.sendMessage(MessageChain().text("修改完成"))

    async def qunyouquanxian(self, request):
        data = request.getFirstTextSplit()
        groupid = request.getGroupId()
        try:
            target = str(int(data[1]))
        except Exception as e:
            await request.sendMessage(MessageChain().text("你这什么QQ啊"))
            return
        if len(data) < 4:
            await request.sendMessage(MessageChain().text("缺少参数"))
            return
        cookie = getCookieByDict(groupid)
        if "groupMemberPermission" not in cookie:
            cookie["groupMemberPermission"] = {}
        if target not in cookie["groupMemberPermission"]:
            cookie["groupMemberPermission"][target] = []
        if data[2] == "add":
            cookie["groupMemberPermission"][target].append(data[3])
        elif data[2] == "remove":
            if data[3] in cookie["groupMemberPermission"][target]:
                cookie["groupMemberPermission"][target].remove(data[3])
        else:
            await request.sendMessage(MessageChain().text("错误操作"))
            return
        setCookieByDict(groupid, cookie)
        await request.sendMessage(MessageChain().text("修改完成"))

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
