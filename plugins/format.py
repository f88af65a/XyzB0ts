from botsdk.tool.MessageChain import MessageChain
from botsdk.BotRequest import BotRequest
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.Error import *
from botsdk.tool.Cookie import *

class formatDict(dict):
    def __missing__(self, key):
        return f"{{{key}}}"

class plugin(BotPlugin):
    "/format [key=word]"

    def __init__(self):
        super().__init__()
        self.name = "format"
        self.addTarget("GroupMessage", "format", self.setFormat)
        self.addFormat(self.doFormat)

    async def doFormat(self, request: BotRequest):
        cookie = getCookie(request.getGroupId(), "format")
        if cookie is None:
            return
        request.getFirst("Plain")["text"] = request.getFirst("Plain")["text"].format_map(formagtDict(cookie))

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
            if len(data[i]) != 2:
                await request.sendMessage(MessageChain().plain("格式有误"))
                return
        cookie = getCookie(request.getGroupId(), "format")
        if cookie is None:
            cookie = {}
        for i in data:
            cookie[i[0]] = i[1]
        setCookie(request.getGroupId(), "format", cookie)
        await request.sendMessage(MessageChain().plain("修改完成"))

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)