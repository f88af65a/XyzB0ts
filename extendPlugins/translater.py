import hashlib
import json
import random
import urllib.parse

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "baidufanyi"
        self.addTarget("GroupMessage", "翻译", self.translater)
        self.addTarget("GroupMessage", "fanyi", self.translater)
        self.addBotType("Mirai")
        self.canDetach = True

    def init(self):
        self.api = self.getConfig()["api"]
        self.appid = self.getConfig()["appid"]
        self.passwd = self.getConfig()["passwd"]

    def makeSign(self, q, salt):
        return hashlib.md5(
                f'''{self.appid}{q}{salt}{self.passwd}'''.encode()
                ).hexdigest()

    def makeUrl(self, data):
        url = self.api
        joinList = []
        for i in data:
            if i == "q":
                joinList.append(f"{i}={urllib.parse.quote(data[i])}")
            else:
                joinList.append(f"{i}={data[i]}")
        return url + "&".join(joinList)

    async def translater(self, request):
        '''fanyi [带空格的文本] #进行一次翻译'''
        requestData = request.getFirstTextSplit()
        if len(requestData) < 2:
            await request.sendMessage(self.translater.__doc__)
            return
        text = " ".join(requestData[1:])
        text = text.replace("\r", "")
        text = text.replace("\n", "")
        salt = random.randint(0, 65535)
        apiRequestData = {
            "q": text,
            "from": "en",
            "to": "zh",
            "appid": self.appid,
            "salt": salt,
            "sign": self.makeSign(text, salt)
        }
        requestUrl = self.makeUrl(apiRequestData)
        apiResponse = await get(requestUrl)
        if apiResponse is None:
            await request.sendMessage("请求失败")
        apiResponse = json.loads(apiResponse)
        if ("trans_result" in apiResponse
                and len(apiResponse["trans_result"]) > 0):
            await request.sendMessage(apiResponse["trans_result"][0]["dst"])


def handle():
    return plugin()
