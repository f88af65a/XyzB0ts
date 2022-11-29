from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    '''撤回消息'''
    def onLoad(self):
        self.addBotType("Mirai")
        self.name = "recall"
        self.addTarget("GroupMessage", "recall", self.recall)

    async def recall(self, request):
        '''#recall 撤回被回复的消息'''
        message = request.getMessageChain()
        for i in message[1:]:
            if i["type"] == "Quote":
                bot = request.getBot()
                quoteMessageId = i["id"]
                try:
                    await bot.recall(quoteMessageId)
                    await request.sendMessage("撤回成功")
                except Exception:
                    await request.sendMessage("撤回失败")
                return
        await request.sendMessage(
            "能撤回吗，没有这个能力，再发下去，要输越南了，回复都不会，找个班上吧。"
            )


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
