from botsdk.BotRequest import BotRequest
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.MessageChain import MessageChain


class formatDict(dict):
    def __missing__(self, key):
        return f"{{{key}}}"


class plugin(BotPlugin):
    "/format key=word;key=word..."

    def __init__(self):
        super().__init__()
        self.name = "format"
        self.addTarget("GroupMessage", "format", self.setFormat)
        self.addFormat(self.doFormat)

    async def doFormat(self, request: BotRequest):
        if request.getType() == "GroupMessage":
            cookie = request.getCookie("format")
            if cookie is None:
                return
            request.getFirst("Plain")["text"] = (
                request.getFirst("Plain")["text"]
                .format_map(formatDict(cookie))
                )

    async def setFormat(self, request: BotRequest):
        "/format [key=word]"
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.sendMessage(MessageChain().plain("参数呢"))
            return
        data = data[1].split(";")
        for i in range(len(data)):
            if data[i] == "":
                await request.sendMessage(MessageChain().plain("格式有误"))
            data[i] = data[i].split("=")
            if len(data[i]) != 2 or data[i][0] == "":
                await request.sendMessage(MessageChain().plain("格式有误"))
                return
        cookie = request.getCookie("format")
        if cookie is None:
            cookie = {}
        for i in data:
            if i[1] == "":
                if i[0] in cookie:
                    del cookie[i[0]]
            else:
                cookie[i[0]] = i[1]
        request.setCookie("format", cookie)
        await request.sendMessage(MessageChain().plain("修改完成"))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
