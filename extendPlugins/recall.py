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
                ret = await bot.recall(
                    quoteMessageId,
                    request.getId().split(":")[-1]
                )
                if ret is not None and "code" in ret and ret["code"] == 0:
                    await request.sendMessage("撤回成功")
                else:
                    await request.sendMessage("撤回失败")
                return
        await request.sendMessage(
            "????"
            )


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
