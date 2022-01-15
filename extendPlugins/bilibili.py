import asyncio
import copy
import json
import time

from botsdk.util.BotNotifyModule import getNotifyModule
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Error import printTraceBack
from botsdk.util.HttpRequest import get


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "bilibili"
        self.addTarget("GroupMessage", "anime", self.anime)
        self.addTarget("GroupMessage", "follower", self.follower)
        self.addBotType("Mirai")

    def init(self, bot):
        for i in self.getConfig()["listen"]:
            self.addFuture(i, self.bilibiliGetDynamic(bot, i))

    async def toNotify(self, notifyName, bot, messageChain):
        notifyModule = getNotifyModule()
        notifySet = copy.deepcopy(notifyModule.notify(notifyName))
        for i in notifySet:
            await bot.sendMessageById(i, messageChain)

    def dynamicCardAnlysis(self, jdata, msg):
        if "vest" in jdata:
            msg.text("[动态][UP:{0}]\n".format(jdata["user"]["uname"]
                     + jdata["sketch"]["title"])
                     + "\n" + jdata["sketch"]["desc_text"])
        elif "title" in jdata:
            if "summary" in jdata:
                msg.text(
                    "[文章][UP:{0}]\n".format(jdata["author"]["name"])
                    + jdata["title"])
            else:
                if "owner" in jdata:
                    msg.text("[视频][UP:{0}]\n".format(jdata["owner"]["name"])
                             + jdata["title"])
                if "pic" in jdata:
                    msg.image(url=jdata["pic"])
                    msg.text("\n")
                if "short_link" in jdata:
                    msg.text("\n" + jdata["short_link"])
        elif "item" in jdata:
            if "origin" in jdata:
                msg.text("[转发][UP:{0}]\n".format(jdata["user"]["uname"])
                         + jdata["item"]["content"] + "\n")
                self.dynamicCardAnlysis(json.loads(jdata["origin"]), msg)
            elif "description" in jdata["item"]:
                msg.text("[动态][UP:{0}]\n".format(jdata["user"]["name"])
                         + jdata["item"]["description"])
                if ("pictures_count" in jdata["item"]
                        and jdata["item"]["pictures_count"] != 0):
                    msg.image(url=jdata["item"]["pictures"][0]["img_src"])
            elif "content" in jdata["item"]:
                msg.text("[UP:{0}]\n".format(jdata["user"]["uname"])
                         + jdata["item"]["content"])
            else:
                msg.text("\n是未识别类型的新动态")

    async def bilibiliGetDynamic(self, bot, uid):
        dynamicId = set()
        maxDynamicId = 0
        notifyName = f"bilibili.dynamic.{uid}"
        while True:
            await asyncio.sleep(30)
            try:
                data = await get(
                    "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/"
                    f"space_history?host_uid={uid}&offset_dynamic_id=0&need_t"
                    "op=1&platform=web")
                if data is None:
                    continue
                data = json.loads(data)
                if data["code"] != 0:
                    continue
                datas = data["data"]["cards"]
                if len(dynamicId) == 0:
                    for i in datas:
                        dynamicId.add(i["desc"]["dynamic_id"])
                else:
                    localId = []
                    for i in datas:
                        localId.append(i["desc"]["dynamic_id"])
                        if (i["desc"]["dynamic_id"] not in dynamicId
                                and i["desc"]["dynamic_id"] > maxDynamicId):
                            dynamicChain = bot.makeMessageChain()
                            self.dynamicCardAnlysis(
                                json.loads(i["card"]), dynamicChain)
                            await self.toNotify(
                                notifyName, bot,
                                bot.makeMessageChain().text("[是新动态捏]")
                                + dynamicChain)
                            dynamicId.add(i["desc"]["dynamic_id"])
                    maxDynamicId = max(maxDynamicId, max(localId))
                    dynamicId = set(localId)
            except Exception:
                printTraceBack()

    async def anime(self, request):
        response = await get(
            "https://bangumi.bilibili.com/web_api/timeline_global")
        if response is None:
            await request.sendMessage("请求失败")
            return
        response = json.loads(response)
        if response["code"] != 0:
            await request.sendMessage("叔叔返回了一个错误")
            return
        response = response["result"]
        thisTime = time.localtime(time.time())
        dayTime = str(thisTime[1]) + "-" + str(thisTime[2])
        for i in response:
            if i["date"] == dayTime:
                printData = "数据来自睿站 现在波特时间{0}:{1}:{2}".format(
                    thisTime[3], thisTime[4], thisTime[5])
                for j in i["seasons"]:
                    if "pub_index" not in j or "pub_time" not in j:
                        continue
                    printData += ("\n" + j["title"] + " "
                                  + j["pub_index"] + " " + j["pub_time"])
                await request.sendMessage(printData)
                return

    async def follower(self, request):
        data = request.getFirstTextSplit()
        if len(data) < 2:
            request.sendMessage("uid呢，uid在哪里")
            return
        response = await get(
            f"https://api.bilibili.com/x/relation/stat?vmid={data[1]}")
        if response is None:
            await request.sendMessage("请求失败")
            return
        response = json.loads(response)
        if response["code"] != 0:
            await request.sendMessage("叔叔返回了一个错误")
            return
        await request.sendMessage(f'''现有粉丝{response["data"]["follower"]}''')


def handle():
    return plugin()
