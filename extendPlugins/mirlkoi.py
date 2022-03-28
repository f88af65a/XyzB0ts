import json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    '''https://iw233.cn/ 提供的api'''
    def onLoad(self):
        self.addBotType("Mirai")
        self.name = "mirlkoi"
        self.addTarget("GroupMessage", "mirlkoi.random", self.randomImg)
        self.addTarget("GroupMessage", "mirlkoi", self.mirlkoiImg)
        self.canDetach = True

    async def randomImg(self, request):
        pass

    async def mirlkoiImg(self, request):
        pass


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
