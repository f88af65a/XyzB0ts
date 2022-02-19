from botsdk.util.BotPlugin import BotPlugin


class handle(BotPlugin):
    def onLoad(self):
        self.name = "QA"
        self.addTarget("GroupMessage", "q&a", self.qaSet)
        self.addFormat(self.checkMessage)
        self.addBotType("Mirai")
        self.canDetach = True

    async def checkMessage(self, request):
        cookie = request.getCookie("q&a")
        if cookie is None:
            return
        keyWord = list(cookie.keys())
        msg = request.getFirstText()
        if not msg:
            return
        for i in keyWord:
            if i in msg:
                request.sendMessage(cookie[i])

    async def qaSet(self, request):
        "q&a [set/del] [关键字] [遇到关键字时触发的消息]"
        data = request.getFirstTextSplit()
        if len(data) == 1:
            await request.sendMessage("q&a [add/del] [关键字] [遇到关键字时触发的消息]")
            return
        if len(data) > 4:
            data = data[0:3] + [" ".join(data[4:])]
        cookie = request.getCookie("q&a")
        if cookie is None:
            cookie = dict()
        if len(data) == 4 and data[1] == "set":
            cookie[data[2]] = data[3]
            request.setCookie("q&a", cookie)
        elif len(data) == 3 and data[1] == "del":
            if data[2] in cookie:
                del cookie[data[2]]
                request.setCookie("q&a", cookie)
        else:
            await request.sendMessage("q&a [add/del] [关键字] [遇到关键字时触发的消息]")
