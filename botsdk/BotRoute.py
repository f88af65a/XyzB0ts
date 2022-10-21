import asyncio

from .BotModule.Request import Request
from .util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from .util.Error import asyncTraceBack
from .util.TimeTest import asyncTimeTest
from .util.BotPluginsManager import BotPluginsManager


class BotRoute:
    def __init__(self):
        self.pluginsManager = BotPluginsManager()
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]

    @asyncTraceBack
    @asyncTimeTest
    async def route(self, request: Request):
        for i in range(len(self.router)):
            if (re := await self.router[i].route(
                    self.pluginsManager, request,
                    None)) is not None and re is False:
                return
            await asyncio.sleep(0)

    def getBot(self):
        return self.bot

    def run(self):
        asyncio.run(self.route())
