import json

from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "cookie"
        self.addTarget("GroupMessage", "cookie", self.cookie)
        self.addTarget("GROUP:1", "cookie", self.cookie)
        self.addTarget("GroupMessage", "id", self.id)
        self.addTarget("GROUP:1", "id", self.id)
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.canDetach = True

    async def cookie(self, request):
        cookie = request.getCookie()
        await request.sendMessage(json.dumps(cookie))

    async def id(self, request):
        await request.sendMessage(
            f"""{request.getId()} {request.getUserId()}""")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
