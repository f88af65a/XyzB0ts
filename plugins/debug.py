import botsdk.Bot
import botsdk.BotRequest
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.Permission import permissionCmp
from botsdk.tool.JsonConfig import getConfig

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.listenType = []
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenTarget = [
                ]
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.filterList = [self.deBugGroupCheck]
        self.name = "debug"
        #"插件名称"
        self.info = "debug过滤"
        #"插件信息"
        self.help = "没有help"
        #"插件帮助"

    def deBugGroupCheck(self, request):
        if getConfig()["debug"]:
            if request.getType() == "GroupMessage" and request.getGroupId() in getConfig()["deBugGroupId"]:
                return True
            return False
        return True

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
