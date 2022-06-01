import json
import copy
from botsdk.util.BotPlugin import BotPlugin


class handle(BotPlugin):
    def onLoad(self):
        self.name = "QA"
        self.addTarget("GroupMessage", "q&a", self.qaSet)
        self.addFormat(self.checkMessage)
        self.addBotType("Mirai")
        self.canDetach = True
        self.cache = dict()

    def makeMapByList(self, keyList):
        if (jsonKeyList := json.dumps(keyList)) in self.cache:
            return self.cache[jsonKeyList]
        tot = 1
        tree = list()
        tree.append(dict())
        firstChar = dict()
        for _ in range(1):
            for i in keyList:
                if len(i) == 0:
                    continue
                startList = list()
                if i[0] in firstChar:
                    startList += firstChar[i[0]]
                if i[0] not in tree[0]:
                    tree.append(dict())
                    tree[0][i[0]] = tot
                    if i[0] not in firstChar:
                        firstChar[i[0]] = list()
                    firstChar[i[0]].append(tot)
                    startList.append(tot)
                    tot += 1
                for j in startList:
                    nodeMark = j
                    for k in range(1, len(i)):
                        if i[k] not in tree[nodeMark]:
                            tree.append(dict())
                            tree[nodeMark][i[k]] = tot
                            if i[k] not in firstChar:
                                firstChar[i[k]] = list()
                            firstChar[i[k]].append(tot)
                            tot += 1
                        nodeMark = tree[nodeMark][i[k]]
                    if "end" not in tree[nodeMark]:
                        tree[nodeMark]["end"] = set()
                    tree[nodeMark]["end"].add(i)
        self.cache[jsonKeyList] = tree
        return tree

    async def checkMessage(self, request):
        msg = request.getFirstText()
        if not msg or not request.isMessage():
            return
        cookie = request.getCookie("q&a")
        if cookie is None:
            return
        keyList = list(cookie.keys())
        keyList.sort()
        keyTree = self.makeMapByList(keyList)
        hitSet = set()
        for j in range(len(msg)):
            nodeMark = 0
            breakFlag = False
            for i in msg[j:]:
                if "end" in keyTree[nodeMark]:
                    hitSet |= keyTree[nodeMark]["end"]
                    breakFlag = True
                    break
                if i not in keyTree[nodeMark]:
                    break
                nodeMark = keyTree[nodeMark][i]
            if breakFlag:
                break
        if "end" in keyTree[nodeMark]:
            hitSet |= keyTree[nodeMark]["end"]
        for i in hitSet:
            try:
                messageChain = json.loads(cookie[i])
            except Exception:
                messageChain = cookie[i]
            await request.sendMessage(messageChain)

    async def qaSet(self, request):
        '''q&a [set/del/all/help] [关键字] [遇到关键字时触发的消息]'''
        data = request.getFirstTextSplit()
        if len(data) == 1:
            await request.sendMessage(self.qaSet.__doc__)
            return
        if len(data) > 4:
            data = data[0:3] + [" ".join(data[4:])]
        cookie = request.getCookie("q&a")
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
                    request.setCookie("q&a", cookie)
                    await request.sendMessage("删除成功")
                    return
                await request.sendMessage("关键字不存在")
            elif data[1] == "set":
                messageChain = request.getMessageChain()
                for i in messageChain:
                    if i["type"] == "Quote":
                        bot = request.getBot()
                        quoteMessageId = i["id"]
                        quoteMessageChain = await bot.messageFromId(
                            quoteMessageId)
                        quoteMessageChain = (
                            quoteMessageChain["data"]["messageChain"][1:])
                        qaMessageChain = []
                        for j in quoteMessageChain:
                            qaMessageChain.append(copy.deepcopy(j))
                            if j["type"] == "Image":
                                if "url" in qaMessageChain[-1]:
                                    del qaMessageChain[-1]["url"]
                cookie[data[2]] = json.dumps(qaMessageChain)
                request.setCookie("q&a", cookie)
                await request.sendMessage("设置成功")
        elif len(data) == 4 and data[1] == "set":
            cookie[data[2]] = data[3]
            request.setCookie("q&a", cookie)
            await request.sendMessage("设置成功")
        else:
            await request.sendMessage(self.qaSet.__doc__)
