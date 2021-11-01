import json
import botsdk.Bot
import botsdk.BotRequest
from botsdk.util.MessageChain import MessageChain
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Cookie import *

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "cookie"
        self.addTarget("GroupMessage", "cookie", self.cookie)
        self.permissionSet = {"OWNER","ADMINISTRATOR","MEMBER"}

    async def cookie(self, request):
        cookie = request.getCookie()
        await request.sendMessage(MessageChain().text(json.dumps(cookie)))

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)