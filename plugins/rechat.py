import botsdk.BotRequest
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.Cookie import *

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.listenType = [["GroupMessage", self.rechat]]
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenTarget = [["GroupMessage", "复读机", self.fuduji]]
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.name = "rechat"
        #"插件名称"
        self.info = "复读机谁不爱啊"
        #"插件信息"
        self.help = "/复读机 [开启/关闭]"
        #"插件帮助"
        self.permissionSet = {"OWNER","ADMINISTRATOR","MEMBER"}
        self.reChatDict = {}

    async def rechat(self, request):
        bot = request.bot
        groupid = request.groupId
        cookie = getCookieByDict(groupid)
        if "rechatState" in cookie and cookie["rechatState"] == "开启":
            chain = []
            for i in request.getMessageChain()[1:]:
                chain.append(dict())
                for j in i:
                    if not (i["type"] == "Image" and j == "url"):
                        chain[-1][j] = i[j]
            if groupid not in self.reChatDict:
                self.reChatDict[groupid] = chain
            elif self.reChatDict[groupid] == chain:
                await bot.sendGroupMessage(groupid, chain)
            else:
                self.reChatDict[groupid] = chain

    async def fuduji(self, request):
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.sendMessage(MessageChain().text("/复读机 [开启/关闭]"))
            return
        groupid = request.groupId
        cookie = getCookieByDict(groupid)
        if "rechatState" not in cookie:
            cookie["rechatState"] = "关闭"
        oldState = cookie["rechatState"]
        newState = data[1]
        if newState != "开启" and newState != "关闭":
            await request.sendMessage(MessageChain().text("会不会用啊"))
            return
        if oldState != newState:
            cookie["rechatState"] = newState
            changeCookieByDict(groupid, cookie)
        await request.sendMessage(MessageChain().text("修改完成"))

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
