from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "botControl"
        self.addTarget("GroupMessage", "quitGroup", self.quitGroup)
        self.addBotType("Mirai")

    async def quitGroup(self, request):
        '''quit q群 #退出q群'''
        request.getBot().quit(request.getFirstTextSplit()[1])


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
