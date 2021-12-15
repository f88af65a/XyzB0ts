from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.JsonConfig import getConfig


class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "debug"
        self.addFilter(self.deBugGroupCheck)

    async def deBugGroupCheck(self, request):
        if getConfig()["debug"]:
            if (request.getType() == "GroupMessage"
                    and request.getGroupId() in getConfig()["deBugGroupId"]):
                return True
            return False
        return True


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
