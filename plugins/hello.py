from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    "/hello"

    def onLoad(self):
        self.name = "hello"
        self.addTarget("GROUP:1", "hello", self.hello)
        self.addBotType("Kaiheila")
        self.canDetach = True

    async def hello(self, request):
        "#hello"
        request.sendMessage("hello")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
