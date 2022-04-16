from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    '''撤回消息'''
    def onLoad(self):
        self.addBotType("Mirai")
        self.name = "fannei"
        self.addTarget("GroupMessage", "fannei", self.fannei)
        self.addFilter(self.wulusai)
        self.canDetach = True

    async def wulusai(self, request):
        if ((not request.isMessage())
                or (cookie := request.getCookie("fannei")) is None):
            return True
        try:
            if request.getUserId() in cookie:
                quoteMessageId = request.getMessageChain()[0]["id"]
                bot = request.getBot()
                await bot.recall(quoteMessageId)
                return False
            else:
                return True
        except Exception:
            return False

    async def fannei(self, request):
        '''fannei #add/del 目标ID'''
        data = request.getFirstTextSplit()
        if len(data) != 3:
            await request.sendMessage(self.fannei.__doc__)
            return
        cookie = request.getCookie("fannei")
        if cookie is None:
            cookie = []
        data[2] = request.userFormat(data[2])
        if data[1] == "add":
            if data[2] not in cookie:
                cookie.append(data[2])
                request.setCookie("fannei", cookie)
        elif data[1] == "del":
            if data[2] in cookie:
                cookie.remove(data[2])
                request.setCookie("fannei", cookie)
        else:
            await request.sendMessage(self.fannei.__doc__)
            return
        await request.sendMessage("成功")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
