from botsdk.util.BotPlugin import BotPlugin


class formatDict(dict):
    def __missing__(self, key):
        return f"{{{key}}}"


class plugin(BotPlugin):
    "/format key=word;key=word..."

    def onLoad(self):
        self.name = "format"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "format", self.setFormat)
        self.addTarget("GROUP:9", "format", self.setFormat)
        self.addTarget("GroupMessage", "say", self.say)
        self.addTarget("GROUP:9", "say", self.say)
        self.addFormat(self.doFormat)
        self.canDetach = True

    async def doFormat(self, request):
        if ((re := request.getFirstText()) is None or not re
           or (cookie := await request.AsyncGetCookie("format")) is None):
            return
        try:
            request.setFirstText(
                    request.getFirstText()
                    .format_map(formatDict(cookie))
                )
        except Exception:
            pass

    async def setFormat(self, request):
        "format [key=word]"
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.sendMessage(self.setFormat.__doc__)
            return
        data = data[1].split(";")
        for i in range(len(data)):
            if data[i] == "":
                await request.sendMessage(
                    request.makeMessageChain().plain("格式有误"))
            data[i] = data[i].split("=")
            if len(data[i]) != 2 or data[i][0] == "":
                await request.sendMessage("格式有误")
                return
        cookie = await request.AsyncGetCookie("format")
        if cookie is None:
            cookie = {}
        for i in data:
            if i[1] == "":
                if i[0] in cookie:
                    del cookie[i[0]]
            else:
                cookie[i[0]] = i[1]
        await request.AsyncSetCookie("format", cookie)
        await request.sendMessage("修改完成")

    async def say(self, request):
        '''say [文本] #让bot复读消息'''
        await request.sendMessage(request.getFirstText())


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
