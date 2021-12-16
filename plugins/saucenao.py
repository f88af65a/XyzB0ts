import json
from botsdk.util.MessageChain import MessageChain
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "saucenao"
        self.addTarget("GroupMessage", "saucenao", self.saucenao)
        self.saucenaoUrl = (
            "https://saucenao.com/search.php?db=999&"
            "output_type=2&numres=16&api_key={key}&url={url}"
        )
        self.key = None
        self.canDetach = True

    def init(self, bot):
        self.key = self.getConfig()["saucenaoKey"]

    async def saucenao(self, request):
        message = request.getMessageChain()
        for i in message[1:]:
            if i["type"] == "Image":
                re = await self.search(i["url"])
                await request.sendMessage(re)
                return
            if i["type"] == "Quote":
                bot = request.getBot()
                quoteMessageId = i["id"]
                quoteMessageChain = await bot.messageFromId(quoteMessageId)
                if quoteMessageChain["code"] != 0:
                    await request.sendMessage(MessageChain().text("消息不在缓存中"))
                    return
                quoteMessageChain = (
                    quoteMessageChain["data"]["messageChain"][1:])
                for j in quoteMessageChain:
                    if j["type"] == "Image":
                        re = await self.search(j["url"])
                        await request.sendMessage(re, request.getMessageId())
                        return
                await request.sendMessage(MessageChain().text("回复消息中没有图片"))
                return
        await request.sendMessage(
            MessageChain().text("未找到图片或参数不为图片(hxd你连发图都不会了🐎)"))

    async def search(self, url):
        searchUrl = self.saucenaoUrl.format(key=self.key, url=url)
        response = json.loads(await get(searchUrl))
        printData = MessageChain()
        if response is None:
            await printData.text("超时或格式错误")
            return printData
        if ("header" not in response
                or "status" not in response["header"]
                or response["header"]["status"] != 0):
            printData.text("又返回了一个错误")
            return printData
        if len(response["results"]) == 0:
            printData.text("无相似图片")
            return printData
        printData.text(
            "返回了{0}张结果\n相似度大于80%的结果".format(len(response["results"])))
        for i in range(0, len(response["results"])):
            if float(response["results"][i]["header"]["similarity"]) < 80:
                continue
            if "member_name" in response["results"][i]["data"]:
                printData.text("\n[作者]{0}".format(
                    response["results"][i]["data"]["member_name"]))
            if "member_id" in response["results"][i]["data"]:
                printData.text("\n[作者ID]{0}".format(
                    response["results"][i]["data"]["member_id"]))
            if "title" in response["results"][i]["data"]:
                printData.text("\n[标题]{0}".format(
                    response["results"][i]["data"]["title"]))
            if "pixiv_id" in response["results"][i]["data"]:
                printData.text("\n[pixiv_id]{0}".format(
                    response["results"][i]["data"]["pixiv_id"]))
                printData.text("\n[相似度]{0}".format(
                    response["results"][i]["header"]["similarity"]))
            if "ext_urls" in response["results"][i]["data"]:
                printData.text("\n[链接]{0}".format(
                    response["results"][i]["data"]["ext_urls"][0]))
        printData.text("\n相似度大于60%的结果")
        for i in range(0, len(response["results"])):
            if (float(response["results"][i]["header"]["similarity"]) >= 80
                    or (float(response["results"][i]["header"]["similarity"])
                        < 60)):
                continue
            if "member_name" in response["results"][i]["data"]:
                printData.text("\n[作者]{0}".format(
                    response["results"][i]["data"]["member_name"]))
            if "member_id" in response["results"][i]["data"]:
                printData.text("\n[作者ID]{0}".format(
                    response["results"][i]["data"]["member_id"]))
            if "title" in response["results"][i]["data"]:
                printData.text("\n[标题]{0}".format(
                    response["results"][i]["data"]["title"]))
            if "pixiv_id" in response["results"][i]["data"]:
                printData.text("\n[pixiv_id]{0}".format(
                    response["results"][i]["data"]["pixiv_id"]))
                printData.text("\n[相似度]{0}".format(
                    response["results"][i]["header"]["similarity"]))
            if "ext_urls" in response["results"][i]["data"]:
                printData.text("\n[链接]{0}".format(
                    response["results"][i]["data"]["ext_urls"][0]))
        return printData


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
