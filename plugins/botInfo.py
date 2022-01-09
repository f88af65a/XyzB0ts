from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    "来自XyzB0ts\n项目地址https://github.com/f88af65a/XyzB0ts"
    def onLoad(self):
        self.name = "botInfo"
        self.addBotType("Mirai")
        self.canDetach = True

    def botinfo(self, request):
        request.sendMessage(request.makeMessageChain().plain(
            "来自XyzB0ts\n项目地址https://github.com/f88af65a/XyzB0ts"))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
