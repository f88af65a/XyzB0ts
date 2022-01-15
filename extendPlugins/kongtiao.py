from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.listenType = []
        self.listenTarget = [["GroupMessage", "空调", self.kongtiao]]
        self.name = "空调"
        self.info = "好热哦"
        self.help = "/空调"
        self.addBotType("Mirai")
        self.canDetach = True

    async def kongtiao(self, request):
        bot = request.bot
        await bot.sendGroupMessage(
            request.getGroupId(),
            request.makeMessageChain()
            .text("https://ac.yunyoujun.cn/#/").getData())


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
