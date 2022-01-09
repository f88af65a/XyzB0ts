import json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.BotModule.MessageChain import MessageChain


class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "cookie"
        self.addTarget("GroupMessage", "cookie", self.cookie)
        self.permissionSet = {"OWNER", "ADMINISTRATOR", "MEMBER"}
        self.canDetach = True

    async def cookie(self, request):
        cookie = request.getCookie()
        await request.sendMessage(MessageChain().text(json.dumps(cookie)))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
