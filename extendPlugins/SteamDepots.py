import json
import time

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "steamdepots"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "depots", self.depots)
        self.addTarget("GROUP:9", "depots", self.depots)
        self.apiUrl = "https://api.steamcmd.net/v1/info/{}"

    async def depots(self, request):
        '''depots [app_id]'''
        requestData = request.getFirstTextSplit()
        if len(requestData) == 1:
            await request.sendMessage(self.depots.__doc__)
            return
        try:
            request_app_id = requestData[1]
        except Exception:
            await request.send("冷知识,app id是数字")
            return
        result = await get(self.apiUrl.format(request_app_id))
        if result is None:
            await request.send("请求失败")
            return
        ret_msg = []
        while True:
            apiResponse = json.loads(result)
            if ("status" not in apiResponse
                    or apiResponse["status"] == "error"):
                ret_msg += ["服务端报错"]
                break
            try:
                branches = (apiResponse["data"][request_app_id]
                                ["depots"]["branches"])
            except Exception:
                ret_msg += ["格式解析出错"]
                break
            ret_msg += [f"来自{request_app_id}的仓库信息"]
            for i in branches.keys():
                depots_msg = []
                if "description" not in branches[i]:
                    depots_msg += [f'''{i}:''']
                else:
                    depots_msg += [f'''{i}: {branches[i]["description"]}''']
                update_time = branches[i]["timeupdated"]
                depots_msg += [
                    f'''更新时间:{time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(
                            int(update_time)))}'''
                ]
                ret_msg += ["\n".join(depots_msg)]
            break
        await request.send("\n".join(ret_msg))

def handle():
    return plugin()
