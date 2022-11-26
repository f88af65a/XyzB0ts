import art

from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    '''art'''
    def onLoad(self):
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.name = "art"
        self.addTarget("GroupMessage", "art", self.func)
        self.addTarget("GROUP:9", "art", self.func)
        self.canDetach = True

    async def func(self, request):
        '''art [英文文本] #艺术'''
        data = request.getFirstTextSplit()
        if len(data) == 1:
            await request.send(self.func.__doc__)
            return
        try:
            await request.send(art.text2art(data[1]))
        except Exception as e:
            await request.send(str(e))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
