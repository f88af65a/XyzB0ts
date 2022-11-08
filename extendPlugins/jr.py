import ujson as json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get
from jsonpath import jsonpath


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "jr"
        self.addBotType("Mirai")
        self.addTarget("GroupMessage", "System:Owner:jr", self.jr)
        self.canDetach = True

    async def jr(self, request):
        '''jr url jsonpath #请求'''
        data = request.getFirstTextSplit()
        if len(data) != 3:
            await request.send(self.jr.__doc__)
            return
        try:
            response = await get(data[1])
            response = json.loads(response)
            await request.send(str(jsonpath(response, data[2])))
        except Exception as e:
            await request.send(str(e))
            return


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
