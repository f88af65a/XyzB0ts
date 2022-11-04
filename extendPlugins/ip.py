import ujson as json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "ip-api"
        self.addTarget("GroupMessage", "ip", self.getIpInfo)
        self.addBotType("Mirai")
        self.canDetach = True
        self.api = "http://ip-api.com/json/{}"

    async def getIpInfo(self, request):
        "ip [IP/DOMAIN] #查询信息"
        requestData = request.getFirstTextSplit()
        if len(requestData) == 1:
            await request.sendMessage(self.getIpInfo.__doc__)
            return
        requestIp = requestData[1]
        responseMessage = f"查询:{requestIp}\n"
        apiResponse = await get(self.api.format(requestIp))
        if apiResponse is None:
            responseMessage += "请求失败"
        else:
            try:
                apiResponse = json.loads(apiResponse)
                for i in apiResponse:
                    responseMessage += f'''{i}: {apiResponse[i]}\n'''
            except Exception:
                responseMessage += "返回值解析失败"
        await request.sendMessage(responseMessage)


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
