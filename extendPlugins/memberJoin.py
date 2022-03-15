from botsdk.util.BotPlugin import BotPlugin
import copy
import json


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "memberJoin"
        self.addType("MemberJoinEvent", self.memberJoin)
        self.listenTarget = [[
            "GroupMessage", "setMemberJoin", self.setMemberJoin]]
        self.addBotType("Mirai")
        self.canDetach = True

    async def setMemberJoin(self, request):
        '''回复setMemberJoin来设置加群消息'''
        data = request.getFirstTextSplit()
        if len(data) == 1:
            messageChain = request.getMessageChain()
            isQuote = False
            for i in messageChain:
                if i["type"] == "Quote":
                    isQuote = True
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
            if not isQuote:
                await request.sendMessage(self.setMemberJoin.__doc__)
                return
            cookie = request.getCookie("memberJoin")
            cookie = json.dumps(qaMessageChain)
            request.setCookie("memberJoin", cookie)
            await request.sendMessage("设置成功")
        elif len(data) == 2:
            if data[1] == "del":
                request.setCookie("memberJoin", "")
                await request.sendMessage("设置成功")

    async def memberJoin(self, request):
        cookie = request.getCookie("memberJoin")
        if not cookie:
            return
        request.sendMessage("cookie")


def handle():
    return plugin()
