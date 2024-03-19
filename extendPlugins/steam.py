import ujson as json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "saucenao"
        self.addTarget("GroupMessage", "查时长", self.playtime)
        self.addBotType("Mirai")
        # self.addBotType("Kaiheila")
        self.key = ""
        self.request_url = (
            "https://api.steampowered.com/IPlayerS"
            "ervice/GetOwnedGames/v1/?key="
            f"{self.key}"
            "&steamid={}&include_played_free_games=true"
        )

    async def playtime(self, request):
        '''查成分 [steamid]'''
        requestData = request.getFirstTextSplit()
        if len(requestData) == 1:
            await request.sendMessage(self.playtime.__doc__)
            return
        try:
            request_steamid = requestData[1]
        except Exception:
            await request.send("冷知识,steamid是数字")
            return
        result = await get(self.request_url.format(request_steamid))
        if result is None:
            await request.send("请求失败")
            return
        try:
            result = json.loads(result)
        except Exception:
            await request.send("格式解析失败")
            return
        response = result["response"]
        ret_msg = []
        game_count = response["game_count"]
        ret_msg.append(f"这位sbeam用户共有{game_count}个游戏")
        games = response["games"]
        more_than_1h = 0
        all_time = 0
        for i in games:
            if i["playtime_forever"] >= 60:
                more_than_1h += 1
                all_time += i["playtime_forever"]
        ret_msg.append(f"其中{more_than_1h}款游戏时长超过1h")
        ret_msg.append(f"这些游戏平均时长为{((all_time/more_than_1h)/60):.1f}h")
        await request.send("\n".join(ret_msg))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
