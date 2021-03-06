from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.JsonConfig import getConfig


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "debug"
        self.addFilter(self.deBugGroupCheck)
        self.addBotType("Mirai")

    async def deBugGroupCheck(self, request):
        if getConfig()["debug"]:
            if (request.getType() == "GroupMessage"
                    and request.getGroupId() in getConfig()["deBugGroupId"]):
                return True
            return False
        return True


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
