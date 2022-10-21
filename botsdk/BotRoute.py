import asyncio

from .BotModule.Request import Request
from .util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from .util.Error import asyncTraceBack
from .util.TimeTest import asyncTimeTest


class BotRoute:
    def __init__(self, bot, pluginsManager, botService, concurrentModule=None):
        self.botService = botService
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
            await asyncio.sleep(0)

    def getPluginsManager(self):
        return self.pluginsManager

    def getBot(self):
        return self.bot

    def getBotService(self):
        return self.botService

    def run(self):
        asyncio.run(self.route())
