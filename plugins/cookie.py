import json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Cookie import getCookie, setCookie


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "cookie"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "cookie", self.cookie)
        self.addTarget("GROUP:1", "cookie", self.cookie)
        self.addTarget("GroupMessage", "id", self.id)
        self.addTarget("GROUP:1", "id", self.id)
        self.addTarget("GroupMessage", "acookie", self.adminCookieControl)
        self.addTarget("GROUP:1", "acookie", self.adminCookieControl)
        self.canDetach = True

    async def cookie(self, request):
        cookie = request.getCookie()
        await request.sendMessage(json.dumps(cookie))

    async def id(self, request):
        await request.sendMessage(
            f"""{request.getId()} {request.getUserId()}""")

    async def adminCookieControl(self, request):
        "acookie ID [new cookie]"
        data = request.getFirstText().split(" ")
        if len(data) < 2:
            request.sendMessage("缺少参数")
        elif len(data) == 2:
            request.sendMessage(getCookie(data[1]))
        else:
            try:
                newCookie = data[2].split("=")
                setCookie(data[1], newCookie[0], json.loads(newCookie[1]))
            except Exception:
                request.sendMessage("参数错误")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
