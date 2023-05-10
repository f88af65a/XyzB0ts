import ujson as json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "kookJsonApi"
        self.addTarget("GroupMessage", "kook", self.kook)
        self.addTarget("GroupMessage", "kookset", self.kookSet)
        self.addBotType("Mirai")

    async def kook(self, request):
        "kook [api]"
        if (cookie := await request.AsyncGetCookie("kookJsonApi")) is None:
            await request.send("未设置KookJsonApi")
            return
        response = await get(cookie)
        if response is None:
            await request.send("获取失败")
            return
        for i in range(1):
            try:
                response = json.loads(response)
            except Exception:
                break
            if "name" not in response:
                break
            name = response["name"]
            if "invite_link" not in response:
                break
            link = response["invite_link"]
            if "online_count" not in response:
                break
            onlineSize = response["online_count"]
            if "members" not in response:
                break
            gameDict = {}
            for i in response["members"]:
                if i["activity"] == "":
                    continue
                if i["activity"] not in gameDict:
                    gameDict[i["activity"]] = 0
                gameDict[i["activity"]] += 1
            moreActivity = "无"
            if len(gameDict) != 0:
                gameList = [[gameDict[i], i] for i in gameDict]
                gameList.sort(reverse=True)
                moreActivity = gameList[0][1]
            await request.send(
                f"服务器名称：{name}\n"
                f"服务器链接：{link}\n"
                f"在线人数：{onlineSize}\n"
                f"最多人在玩游戏：{moreActivity} | {gameList[0][0]}"
            )
            return
        await request.send("格式解析失败")

    async def kookSet(self, request):
        """kookset 小工具链接 #设置小工具链接"""
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.kookSet.__doc__)
            return
        await request.AsyncSetCookie("kookJsonApi", data[1])
        await request.send("设置完成")

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
