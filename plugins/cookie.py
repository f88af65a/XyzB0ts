import json

from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "cookie"
        self.addTarget("GroupMessage", "cookie", self.cookie)
        self.addTarget("Group:1", "cookie", self.cookie)
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.canDetach = True

    async def cookie(self, request):
        cookie = request.getCookie()
        await request.sendMessage(json.dumps(cookie))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
