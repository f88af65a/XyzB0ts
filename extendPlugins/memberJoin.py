import copy

import ujson as json

from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "memberJoin"
        self.addType("MemberJoinEvent", self.memberJoin)
        self.addTarget("GroupMessage", "setMemberJoin", self.setMemberJoin)
        self.addTarget("GroupMessage", "delMemberJoin", self.delMemberJoin)
        self.addBotType("Mirai")

    async def delMemberJoin(self, request):
        '''回复delMemberJoin来设置加群消息'''
        cookie = await request.AsyncGetCookie("memberJoin")
        cookie = ""
        await request.AsyncSetCookie("memberJoin", cookie)
        await request.sendMessage("设置成功")

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
            if not isQuote:
                await request.sendMessage(self.setMemberJoin.__doc__)
                return
            cookie = await request.AsyncGetCookie("memberJoin")
            cookie = json.dumps(qaMessageChain)
            await request.AsyncSetCookie("memberJoin", cookie)
            await request.sendMessage("设置成功")

    async def memberJoin(self, request):
        id = (request.getBot().getBotName()
              + ":"
              + request.groupFormat(request["member"]["group"]["id"]))
        cookie = await request.AsyncGetCookie(
            "memberJoin", id
            )
        if not cookie:
            return
        messageChain = (
            request.makeMessageChain().at(request["member"]["id"])
            + request.makeMessageChain(json.loads(cookie))
        )
        await request.sendMessage(
            messageChain.getData(), id=id,
            messageType="GroupMessage"
            )


def handle():
    return plugin()
