import ujson as json
import random

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    '''https://iw233.cn/ 提供的api'''
    def onLoad(self):
        self.name = "mirlkoi"
        self.addBotType("Mirai")
        self.addTarget("GroupMessage", "mirlkoi", self.mirlkoi)
        self.urls = [
            "api.iw233.cn",
            "ap1.iw233.cn",
            "dev.iw233.cn"
        ]
        self.url = "http://{}/api.php?sort=iw233&type=json"

    async def mirlkoi(self, request):
        '''#mirlkoi.random 从mirlkoi获取一张随机图'''
        try:
            ret = json.loads((await get(
                self.url.format(
                    self.urls[random.randint(0, len(self.urls) - 1)]
                    )
            )).encode("utf8"))
            print(ret["pic"])
            await request.send(
                request.makeMessageChain().image(url=ret["pic"][0])
            )
        except Exception:
            await request.sendMessage("获取失败")
            return


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
