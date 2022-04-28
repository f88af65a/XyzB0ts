import botsdk.BotModule.Bot
import botsdk.BotModule.Request
import botsdk.util.JsonConfig
from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "systemHelp"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "config", self.configHelp)
        self.addTarget("GROUP:9", "config", self.configHelp)

    async def configHelp(self, request):
        '''config [reload]'''
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.sendMessage("config [reload]")
            return
        if data[1] == "reload":
            botsdk.util.JsonConfig.reload()
            await request.sendMessage("重新加载完成")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
