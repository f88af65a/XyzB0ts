import json

import botsdk.BotRequest
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.MessageChain import MessageChain


class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "cookie"
        self.addTarget("GroupMessage", "cookie", self.cookie)
        self.permissionSet = {"OWNER", "ADMINISTRATOR", "MEMBER"}

    async def cookie(self, request: botsdk.BotRequest):
        cookie = request.getCookie()
        await request.sendMessage(MessageChain().text(json.dumps(cookie)))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
