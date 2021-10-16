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
        self.listenTarget = [["GroupMessage", "空调", self.kongtiao]]
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.name = "空调"
        #"插件名称"
        self.info = "好热哦"
        #"插件信息"
        self.help = "/空调"
        #"插件帮助"
        self.permissionSet = {"OWNER","ADMINISTRATOR","MEMBER"}
        self.canDetach = True

    async def kongtiao(self, request):
        bot = request.bot
        groupid = request.groupId
        await bot.sendGroupMessage(request.groupId, MessageChain().text("https://ac.yunyoujun.cn/#/").getData())

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
