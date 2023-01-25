from ujson import loads

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    '''bfv'''
    def onLoad(self):
        self.name = "bfv"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "bfv.search", self.search)
        self.addTarget("GROUP:9", "bfv.search", self.search)
        self.addTarget("GroupMessage", "bfv.搜人", self.search)
        self.addTarget("GROUP:9", "bfv.搜人", self.search)
        self.addTarget("GroupMessage", "bfv.server.search", self.serverSearch)
        self.addTarget("GROUP:9", "bfv.server.search", self.serverSearch)
        self.addTarget("GroupMessage", "bfv.搜服", self.serverSearch)
        self.addTarget("GROUP:9", "bfv.搜服", self.serverSearch)

    async def search(self, request):
        '''bfv.search id #查询战绩'''
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.search.__doc__)
            return
        response = await get(
            "https://api.gametools.network/bfv/stats/?"
            f"format_values=true&name={data[1]}"
            "&platform=pc&skip_battlelog=false&lang=en-us"
        )
        if response is None:
            await request.send(f"获取{data[1]}的数据失败")
            return
        try:
            response = loads(response)
        except Exception:
            await request.send(f"解析{data[1]}的数据失败")
            return
        if "errors" in response:
            await request.send(
                "\n".join(response["errors"])
            )
            return
        await request.send(
            f'''{response["userName"]}\n'''
            f'''rank: {response["rank"]}\n'''
            f'''KD: {response["killDeath"]}\n'''
            f'''KPM: {response["killsPerMinute"]}\n'''
            f'''SPM: {response["scorePerMinute"]}\n'''
            f'''命中率: {response["accuracy"]}\n'''
            f'''爆头率: {response["headshots"]}\n'''
            f'''击杀数: {response["kills"]} | {"{:.2f}".format(
                response["kills"]/max(response["roundsPlayed"], 1))}\n'''
            f'''死亡数: {response["deaths"]} | {"{:.2f}".format(
                response["deaths"]/max(response["roundsPlayed"], 1))}\n'''
            f'''最高连杀: {response["highestKillStreak"]}\n'''
            f'''游戏时间: {response["timePlayed"]}'''
        )

    async def serverSearch(self, request):
        '''bfv.server.search 关键字 #查询战绩'''
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.send(self.search.__doc__)
            return
        response = await get(
            "https://api.gametools.network/bfv/servers/?"
            f"name={data[1]}&region=all&platform=pc&limit=10&lang=en-us"
        )
        if response is None:
            await request.send(f"获取{data[1]}的数据失败")
            return
        try:
            response = loads(response)
        except Exception:
            await request.send(f"解析{data[1]}的数据失败")
            return
        if "errors" in response:
            await request.send(
                "\n".join(response["errors"])
            )
            return
        if "servers" not in response:
            await request.send(
                "返回格式有误"
            )
            return
        retMsg = []
        for i in response["servers"]:
            retMsg.append(
                f'''{i["prefix"]}\n'''
                f'''人数: {i["playerAmount"]}/{i["maxPlayers"]}'''
                f''' (+{i["inQue"]})\n'''
                f'''模式: {i["mode"]}\n'''
                f'''地图: {i["currentMap"]}'''
            )
        await request.send("搜到以下服务器\n" + "\n".join(retMsg))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
