from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "chuo"
        self.addType("NudgeEvent", self.nudge)
        self.canDetach = True

    async def nudge(self, request):
        if str(request["target"]) == request.getBot().getQq():
            await request.getBot().sendNudge(target=request["fromId"],
                                             subject=request["subject"]["id"],
                                             kind=request["subject"]["kind"])


def handle():
    return plugin()
