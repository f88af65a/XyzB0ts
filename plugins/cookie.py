import json

from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "cookie"
        self.addTarget("GroupMessage", "cookie", self.cookie)
        self.permissionSet = {"OWNER", "ADMINISTRATOR", "MEMBER"}
        self.addBotType("Mirai")
        self.canDetach = True

    async def cookie(self, request):
        cookie = request.getCookie()
        await request.sendMessage(
            request.makeMessageChain().text(json.dumps(cookie)))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
