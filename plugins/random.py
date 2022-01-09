import random

from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.addBotType("Mirai")
        self.name = "random"
        self.addTarget("GroupMessage", "random", self.random)
        self.canDetach = True

    async def random(self, request):
        "/random 最小值 最大值"
        data = request.getFirstTextSplit()
        if len(data) < 3:
            await request.sendMessage(self.random.__doc__)
            return
        try:
            l, r = int(data[1]), int(data[2])
            if l > r:
                raise
        except Exception:
            await request.sendMessage(self.random.__doc__)
            return
        await request.sendMessage(str(random.randint(l, r)))


def handle():
    return plugin()
