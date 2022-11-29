from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "botInfo"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "bot", self.botinfo)
        self.addTarget("GROUP:9", "bot", self.botinfo)

    async def botinfo(self, request):
        '''bot #打印bot信息'''
        await request.sendMessage(
            "来自XyzB0ts\n项目地址https://github.com/f88af65a/XyzB0ts")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
