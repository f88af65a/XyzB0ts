import ujson as json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "steamapi"
        self.addTarget("GroupMessage", "steam.ban", self.bancheck)
        self.addTarget("GROUP:9", "steam.ban", self.bancheck)
        self.addBotType("Mirai")

    def init(self):
        self.key = self.getConfig()["key"]
        self.proxy = self.getConfig()["proxy"]

    async def bancheck(self, request):
        "steam.ban [steamid(64位id)] #查询steam封禁记录"
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.bancheck.__doc__)
            return
        try:
            int(data[1])
        except Exception:
            await request.send("参数应为steamid(64位id)")
            return
        response = await get(
            "https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?"
            f"key={self.key}"
            f"&steamids={data[1]}",
            proxy=self.proxy
        )
        if response is None:
            await request.send("响应超时")
            return
        try:
            response = json.loads(response)["players"]
        except Exception:
            await request.send("json解析失败")
            return
        if len(response) == 0:
            await request.send("steamid不存在")
            return
        response = response[0]
        await request.send(
            f'''SteamId:{response["SteamId"]}\n'''
            f'''VAC封禁:{"是" if response["VACBanned"] else "否"}\n'''
            f'''VAC封禁次数:{response["NumberOfVACBans"]}\n'''
            f'''上一次被封禁时间:{response["DaysSinceLastBan"]}\n'''
            f'''被开发者封禁次数:{response["NumberOfGameBans"]}\n'''
        )


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
