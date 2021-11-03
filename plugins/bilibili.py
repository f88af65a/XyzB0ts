import copy
from botsdk.Bot import Bot
from botsdk.util.Error import *
from botsdk.util.HttpRequest import *
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.MessageChain import MessageChain
from botsdk.util.BotNotifyModule import getNotifyModule

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "bilibiliData"
    
    def init(self, bot):
        for i in self.getConfig()["listen"]:
            self.addFuture(i, self.bilibiliGetDynamic(bot, i))

    async def toNotify(self, notifyName, bot: Bot, messageChain: MessageChain):
        notifyModule = getNotifyModule()
        notifySet = copy.deepcopy(notifyModule.notify(notifyName))
        for i in notifySet:
            await bot.sendMessageById(i, messageChain)

    def dynamicCardAnlysis(self, jdata):
        msg = MessageChain()
        if "vest" in jdata:
            msg.text("[动态][UP:{0}]\n".format(jdata["user"]["uname"]) + jdata["sketch"]["title"] + "\n" + jdata["sketch"]["desc_text"])
        elif "title" in jdata:
            if "summary" in jdata:
                msg.text("[文章][UP:{0}]\n".format(jdata["author"]["name"]) + jdata["title"])
            else:
                msg.text("[视频][UP:{0}]\n".format(jdata["owner"]["name"]) + jdata["title"])
                if "pic" in jdata:
                    msg.image(url=jdata["pic"])
                    msg.text("\n")
                if "short_link" in jdata:
                    msg.text("\n" + jdata["short_link"])
        elif "item" in jdata:
            if "origin" in jdata:
                msg.text("[转发][UP:{0}]\n".format(jdata["user"]["uname"]) + jdata["item"]["content"] +"\n")
                msg += self.dynamicCardAnlysis(json.loads(jdata["origin"]))
            elif "description" in jdata["item"]:
                msg.text("[动态][UP:{0}]\n".format(jdata["user"]["name"]) + jdata["item"]["description"])
            elif "content" in jdata["item"]:
                msg.text("[UP:{0}]\n".format(jdata["user"]["uname"]) + jdata["item"]["content"])
            else:
                msg.text("\n是未识别类型的新动态")
        return msg

    async def bilibiliGetDynamic(self, bot, uid):
        dynamicId = set()
        maxDynamicId = 0
        notifyName = f"bilibili.dynamic.{uid}"
        try:
            data = await get(f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&offset_dynamic_id=0&need_top=1&platform=web")
            if data is None or data["code"] != 0:
                raise
            datas = data["data"]["cards"]
            if len(dynamicId) == 0:
                for i in datas:
                    dynamicId.add(i["desc"]["dynamic_id"])
            else:
                localId = []
                for i in datas:
                    localId.append(i["desc"]["dynamic_id"])
                    if i["desc"]["dynamic_id"] not in dynamicId and i["desc"]["dynamic_id"] > maxDynamicId:
                        await self.toNotify(notifyName, bot, MessageChain().text("[是新动态捏]") + self.dynamicCardAnlysis(json.loads(i["card"])))
                        dynamicId.add(i["desc"]["dynamic_id"])
                maxDynamicId = max(maxDynamicId,max(localId))
                dynamicId = set(localId)
        except Exception as e:
            printTraceBack()

def handle():
    return plugin()