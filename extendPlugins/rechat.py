from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.addBotType("Mirai")
        self.name = "rechat"
        self.addType("GroupMessage", self.rechat)
        self.addTarget("GroupMessage", "复读机", self.fuduji)
        self.reChatDict = {}

    async def rechat(self, request):
        bot = request.getBot()
        cookie = await request.AsyncGetCookie("rechatState")
        if cookie is not None and cookie["rechatState"] == "开启":
            chain = []
            groupid = request.getGroupId()
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
        '''复读机 [开启/关闭]'''
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.sendMessage(self.fuduji.__doc__)
            return
        cookie = await request.AsyncGetCookie("rechatState")
        if cookie is None:
            cookie = {"rechatState": "关闭"}
        oldState = cookie["rechatState"]
        newState = data[1]
        if newState != "开启" and newState != "关闭":
            await request.sendMessage("会不会用啊")
            return
        if oldState != newState:
            cookie["rechatState"] = newState
            await request.AsyncSetCookie("rechatState", cookie)
        await request.sendMessage("修改完成")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
