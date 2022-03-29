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
        '''#mirlkoi.random 从mirlkoi获取一张随机图'''
        try:
            ret = json.loads((await get("https://iw233.cn/API/Random.php?type=json")).encode("utf8"))
            await request.sendMessage(
                request.makeMessageChain().image(url=ret["pic"]))
        except Exception:
            await request.sendMessage("获取失败")
            return

    async def mirlkoiImg(self, request):
        '''#mirlkoi 从mirlkoi获取一张精品图'''
        try:
            ret = json.loads((await get("https://iw233.cn/API/MirlKoi.php?type=json")).encode("utf8"))
            await request.sendMessage(
                request.makeMessageChain().image(url=ret["pic"]))
        except Exception:
            await request.sendMessage("获取失败")
            return


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
