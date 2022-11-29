import ujson as json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    '''p站相关功能\n/pixiv.[search/rank] [关键字/无] [on]'''
    def onLoad(self):
        self.addBotType("Mirai")
        self.name = "bgps"
        self.addTarget("GroupMessage", "bgps", self.bgps)

    def init(self):
        self.url = (
                "https://best-game-price-search.p.rapidapi.com"
                "/steam/specials?page={}&limit=5&currency=USD"
        )
        self.proxy = self.getConfig()["proxy"]
        self.key = self.getConfig()["X-RapidAPI-Key"]
        self.host = self.getConfig()["X-RapidAPI-Host"]

    async def bgps(self, request):
        '''steam [页数] #查询特惠信息'''
        data = request.getFirstTextSplit()
        if len(data) == 1:
            page = 1
        else:
            try:
                page = int(data[1])
            except Exception:
                await request.send("页数错误")
                return
        response = await get(
                self.url.format(page),
                headers={
                    "X-RapidAPI-Key": self.key,
                    "X-RapidAPI-Host": self.host
                },
                proxy=self.proxy
            )
        if response is None:
            await request.send("请求失败")
            return
        response = json.loads(response)
        if "message" in response:
            await request.send(response["message"])
            return
        responseMessage = "------\n"
        for i in range(len(response["results"])):
            responseMessage += (
                f'''名称:{response["results"][i]["title"]}\n'''
                f'''原价:{response["results"][i]["old_price"]}\n'''
                f'''现价:{response["results"][i]["currency_tag"]}'''
                f'''{response["results"][i]["price"]}\n'''
                f'''折扣:{response["results"][i]["discount"]}\n'''
                f'''发布日期:{response["results"][i]["release_date"]}\n'''
                f'''平台:{response["results"][i]["source"]}\n'''
                f'''链接:{response["results"][i]["url"]}\n'''
            )
            responseMessage += "------"
            if i != len(response["results"]) - 1:
                responseMessage += "\n"
        await request.send(responseMessage)


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
