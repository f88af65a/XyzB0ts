import copy
import time

import ujson as json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Cache import GetCacheInstance


class handle(BotPlugin):
    def onLoad(self):
        self.name = "QA"
        self.addTarget("GroupMessage", "q&a", self.qaSet)
        self.addType("GroupMessage", self.checkMessage)
        self.addBotType("Mirai")
        self.cache = dict()

    def makeTreeByKey(self, keyList):
        tot = 1
        tree = list()
        tree.append(dict())
        for i in keyList:
            if len(i) == 0:
                continue
            node = tree[0]
            for j in i:
                if j not in node:
                    tree.append(dict())
                    node[j] = tot
                    tot += 1
                node = tree[node[j]]
            if "END" not in node:
                node["END"] = i
        return tree

    def checkOnTree(self, tree, key):
        nodeList = [tree[0]]
        for i in key:
            newNodeList = [tree[0]]
            for j in nodeList:
                if "END" in j:
                    return j["END"]
                if i in j:
                    newNodeList.append(tree[j[i]])
            if not len(newNodeList):
                return []
            nodeList = newNodeList
        for i in nodeList:
            if "END" in i:
                return i["END"]
        return None

    async def checkMessage(self, request):
        msg = request.getFirstText()
        if not msg or not request.isMessage():
            return
        cookie = await request.AsyncGetCookie("q&a")
        if cookie is None:
            return
        keyTree = self.makeTreeByKey(
                list(cookie.keys()))
        hit = self.checkOnTree(keyTree, msg)
        if hit is None:
            return
        # CD
        cd = await GetCacheInstance().GetCache(
            f"QA:CD:{request.getId()}"
        )
        if cd is not None:
            return
        await GetCacheInstance().SetCache(
            f"QA:CD:{request.getId()}",
            {"cdTime": str(int(time.time()))},
            2
        )
        try:
            messageChain = json.loads(cookie[hit])
        except Exception:
            messageChain = cookie[hit]
        await request.sendMessage(messageChain)

    async def qaSet(self, request):
        '''q&a [set/del/all/help] [关键字] [遇到关键字时触发的消息]'''
        data = request.getFirstTextSplit()
        if len(data) == 1:
            await request.sendMessage(self.qaSet.__doc__)
            return
        if len(data) > 4:
            data = data[0:3] + [" ".join(data[4:])]
        cookie = await request.AsyncGetCookie("q&a")
        if cookie is None:
            cookie = dict()
        if len(data) == 2:
            if (data[1] == "all" or data[1] == "help"):
                await request.sendMessage(
                    "现有关键字:\n" + "\n".join(list(cookie.keys())))
                return
        elif len(data) == 3:
            if data[1] == "del":
                if data[2] in cookie:
                    del cookie[data[2]]
                    await request.AsyncSetCookie("q&a", cookie)
                    await request.sendMessage("删除成功")
                    return
                await request.sendMessage("关键字不存在")
            elif data[1] == "set":
                if len(data[2]) > 16 or len(data[2]) < 2:
                    await request.send("关键字最短为2字,最长为16字")
                    return
                messageChain = request.getMessageChain()
                quoteMessageChain = None
                for i in messageChain:
                    if i["type"] == "Quote":
                        bot = request.getBot()
                        quoteMessageId = i["id"]
                        quoteMessageChain = await bot.messageFromId(
                            quoteMessageId,
                            request.getGroupId()
                            )
                        quoteMessageChain = (
                            quoteMessageChain["data"]["messageChain"][1:])
                        qaMessageChain = []
                        for j in quoteMessageChain:
                            qaMessageChain.append(copy.deepcopy(j))
                            if j["type"] == "Image":
                                if "url" in qaMessageChain[-1]:
                                    del qaMessageChain[-1]["url"]
                if quoteMessageChain is None:
                    await request.send(self.qaSet.__doc__)
                    return
                cookie[data[2]] = json.dumps(qaMessageChain)
                await request.AsyncSetCookie("q&a", cookie)
                await request.sendMessage("设置成功")
        elif len(data) == 4 and data[1] == "set":
            if len(data[2]) > 16 or len(data[2]) < 2:
                await request.send("关键字最短为2字,最长为16字")
                return
            cookie[data[2]] = data[3]
            await request.AsyncSetCookie("q&a", cookie)
            await request.sendMessage("设置成功")
        else:
            await request.sendMessage(self.qaSet.__doc__)
