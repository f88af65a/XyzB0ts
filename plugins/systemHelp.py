import botsdk.BotModule.Bot
import botsdk.BotModule.Request
import botsdk.util.JsonConfig
from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.name = "systemHelp"
        self.addTarget("GroupMessage", "config", self.configHelp)
        self.addTarget("GROUP:1", "config", self.configHelp)

    async def configHelp(self, request):
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.sendMessage("缺少参数")
            return
        if data[1] == "reload":
            botsdk.util.JsonConfig.reload()
            await request.sendMessage("重新加载完成")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
