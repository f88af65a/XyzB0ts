import json
from botsdk.util.BotPlugin import BotPlugin


class handle(BotPlugin):
    def onLoad(self):
        self.name = "QA"
        self.addTarget("GroupMessage", "q&a", self.qaSet)
        self.addFormat(self.checkMessage)
        self.addBotType("Mirai")
        self.canDetach = True

    async def checkMessage(self, request):
        msg = request.getFirstText()
        if not msg or not request.isMessage():
            return
        cookie = request.getCookie("q&a")
        if cookie is None:
            return
        keyWord = list(cookie.keys())
        for i in keyWord:
            if i in msg:
                try:
                    messageChain = json.loads(cookie[i])
                    bot = request.getBot()
                    groupid = request.getGroupId()
                    await bot.sendGroupMessage(groupid, messageChain)
                except Exception:
                    await request.sendMessage(cookie[i])
                break

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
                await request.sendMessage(",".join(list(cookie.keys())))
                return
        elif len(data) == 3:
            if data[1] == "set":
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
                            qaMessageChain.append(j)
                            if j["type"] == "Image":
                                if "url" in qaMessageChain[j]:
                                    del qaMessageChain[j]["url"]
                cookie[data[2]] = json.dumps(qaMessageChain)
                request.setCookie("q&a", cookie)
                await request.sendMessage("设置成功")
        elif len(data) == 4 and data[1] == "set":
            cookie[data[2]] = data[3]
            request.setCookie("q&a", cookie)
            await request.sendMessage("设置成功")
        elif len(data) == 3 and data[1] == "del":
            if data[2] in cookie:
                del cookie[data[2]]
                request.setCookie("q&a", cookie)
                await request.sendMessage("删除成功")
                return
            await request.sendMessage("不存在")
        else:
            await request.sendMessage("q&a [add/del] [关键字] [遇到关键字时触发的消息]")
