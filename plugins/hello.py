from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    "/hello"

    def onLoad(self):
        self.name = "hello"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GROUP:1", "hello", self.hello)
        self.addTarget("GroupMessage", "hello", self.hello)
        self.addTarget("FriendMessage", "hello", self.hello)
        self.canDetach = True

    async def hello(self, request):
        "hello #hello"
        await request.sendMessage("hello")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
