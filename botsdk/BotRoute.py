from botsdk.util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from botsdk.BotModule.Request import Request
from botsdk.util.TimeTest import asyncTimeTest
from botsdk.util.Error import asyncTraceBack


class BotRoute:
    def __init__(self, bot, pluginsManager, concurrentModule=None):
        self.bot = bot
        self.concurrentModule = concurrentModule
        self.pluginsManager = pluginsManager
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]

    @asyncTraceBack
    @asyncTimeTest
    async def route(self, request: Request):
        for i in range(len(self.router)):
            if (re := await self.router[i].route(
                    self.pluginsManager, request,
                    self.concurrentModule)) is not None and re is False:
                return

    def getPluginsManager(self):
        return self.pluginsManager
