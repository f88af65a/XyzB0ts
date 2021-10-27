from botsdk.BotRequest import BotRequest
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.Cookie import *

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "rechat"
        self.addType("GroupMessage", self.rechat)
        self.addTarget("GroupMessage", "复读机", self.fuduji)
        self.addTarget("GroupMessage", "say", self.say)
        self.reChatDict = {}

    async def rechat(self, request):
        bot = request.getBot()
        groupid = request.getGroupId()
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
        groupid = request.getGroupId()
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
            setCookieByDict(groupid, cookie)
        await request.sendMessage(MessageChain().text("修改完成"))
    
    async def say(self, request: BotRequest):
        chain = []
        for i in request.getMessageChain()[1:]:
                chain.append(dict())
                for j in i:
                    if not (i["type"] == "Image" and j == "url"):
                        chain[-1][j] = i[j]
        await request.getBot().sendMessage(request.getId(), chain)

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
