import json
import botsdk.Bot
import botsdk.BotRequest
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.Cookie import *

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "cookie"
        self.addTarget("GroupMessage", "cookie", self.cookie)
        self.permissionSet = {"OWNER","ADMINISTRATOR","MEMBER"}

    async def cookie(self, request):
        groupid = request.getGroupId()
        cookie = getCookieByDict(groupid)
        await request.sendMessage(MessageChain().text(json.dumps(cookie)))

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)