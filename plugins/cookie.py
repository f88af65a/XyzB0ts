import json
import botsdk.Bot
import botsdk.BotRequest
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.Cookie import *
class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.listenType = []
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenTarget = [["GroupMessage", "cookie", self.cookie]]
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.name = "cookie"
        #"插件名称"
        self.info = "cookie管理"
        #"插件信息"
        self.help = "/cookie"
        #"插件帮助"
        self.permissionSet = {"OWNER","ADMINISTRATOR","MEMBER"}

    async def cookie(self, request):
        groupid = request.getGroupId()
        cookie = getCookieByDict(groupid)
        await request.sendMessage(MessageChain().text(json.dumps(cookie)))

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)