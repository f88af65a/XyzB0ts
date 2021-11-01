import botsdk.Bot
import botsdk.BotRequest
import botsdk.util.JsonConfig
from botsdk.util.MessageChain import MessageChain
from botsdk.util.BotPlugin import BotPlugin

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "systemHelp"
        self.addTarget("GroupMessage", "config", self.configHelp)

    async def configHelp(self, request):
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.sendMessage(MessageChain().text("缺少参数"))
            return
        if data[1] == "reload":
            botsdk.util.JsonConfig.reload()
            await request.sendMessage(MessageChain().text("重新加载完成"))

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)