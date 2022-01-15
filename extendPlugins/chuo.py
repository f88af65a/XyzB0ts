from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "chuo"
        self.addType("NudgeEvent", self.nudge)
        self.addBotType("Mirai")
        self.canDetach = True

    async def nudge(self, request):
        if str(request["target"]) == request.getBot().getQq():
            await request.getBot().sendNudge(target=request["fromId"],
                                             subject=request["subject"]["id"],
                                             kind=request["subject"]["kind"])


def handle():
    return plugin()
