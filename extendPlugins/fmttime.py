import time
from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "fmttime"
        parser = self.addTargetWithArgs("GroupMessage", "time", self.fmttime)
        parser.Add("time", help="时间戳")
        parser = self.addTargetWithArgs("GROUP:9", "time", self.fmttime)
        parser.Add("time", help="时间戳")
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.canDetach = True

    async def fmttime(self, request):
        '''格式化时间'''
        args = request.getArgs()
        try:
            await request.send(
                time.strftime(
                    "%Y-%m-%d %H:%M:%S",
                    time.localtime(int(args["time"])))
                )
        except Exception as e:
            await request.send("输入的时间有误")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
