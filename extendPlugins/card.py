from botsdk.util.BotPlugin import BotPlugin
import random
import math


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "card"
        self.addBotType("Mirai")
        self.addTarget("GroupMessage", "addcard", self.addcard)
        self.addTarget("GroupMessage", "delcard", self.delcard)
        self.addTarget("GroupMessage", "getcard", self.getcard)
        self.addTarget("GroupMessage", "cardsize", self.cardsize)
        self.addTarget("GroupMessage", "listcard", self.listcard)

    async def addcard(self, request):
        "addcard [以半角逗号分隔的文本,最长32位]"
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.sendMessage(self.addcard.__doc__)
            return
        data = data[1].split(",")
        for i in data:
            if len(i) > 32:
                await request.send(f"有文本长度超过32位,{i}")
                return
        cookie = await request.AsyncGetCookie("card")
        if cookie is None:
            cookie = []
        if len(cookie) + len(data) >= 200:
            await request.sendMessage("加入则超过200个,最多储存200个")
            return
        for i in data:
            cookie.append(i)
        await request.AsyncSetCookie("card", cookie)
        await request.sendMessage("修改完成")

    async def delcard(self, request):
        "delcard [以半角逗号分隔的文本,最长32位]"
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.sendMessage(self.setFormat.__doc__)
            return
        data = data[1].split(",")
        for i in data:
            if len(i) > 32:
                await request.send(f"有文本长度超过32位,{i}")
                return
        cookie = await request.AsyncGetCookie("card")
        if cookie is None:
            cookie = []
        okList = []
        for i in data:
            if i in cookie:
                cookie.remove(i)
                okList.append(i)
        await request.AsyncSetCookie("card", cookie)
        await request.sendMessage("成功删除以下card\n" + "\n".join(okList))

    async def getcard(self, request):
        "getcard [需要的card数量,默认为1]"
        data = request.getFirstTextSplit()
        cardSize = 1
        if len(data) == 2:
            try:
                cardSize = int(data[1])
            except Exception:
                await request.send("数量应为数字")
                return
        cookie = await request.AsyncGetCookie("card")
        if cookie is None:
            cookie = []
        if len(cookie) < cardSize:
            await request.send("card数量不足")
            return
        retList = []
        for i in range(cardSize):
            mark = random.randint(0, len(cookie) - 1)
            retList.append(cookie[mark])
            del cookie[mark]
        await request.AsyncSetCookie("card", cookie)
        await request.sendMessage("card:\n" + "\n".join(retList))

    async def cardsize(self, request):
        "cardsize #获取当前card数量"
        cookie = await request.AsyncGetCookie("card")
        if not cookie:
            cookie = []
        await request.sendMessage(f"当前有:{len(cookie)}个card")

    async def listcard(self, request):
        "listcard [页数,默认为1] #查看当前的list,每页最多20个"
        data = request.getFirstTextSplit()
        mark = 1
        if len(data) == 2:
            try:
                mark = int(data[1])
                if mark == 0:
                    mark = 1
            except Exception:
                await request.send("数量应为数字")
                return
        cookie = await request.AsyncGetCookie("card")
        if cookie is None:
            cookie = []
        await request.sendMessage(
            "card:\n" +
            "\n".join(cookie[(mark - 1) * 20: mark * 20]) +
            f"\n当前是第{mark}页，共{math.ceil(len(cookie)/20)}页"
        )


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
