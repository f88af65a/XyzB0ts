from botsdk.util.Error import *
from botsdk.util.JsonConfig import getConfig
from botsdk.util.TimeTest import asyncTimeTest
from botsdk.BotRequest import BotRequest
from botsdk.util.BotPluginsManager import BotPluginsManager
from botsdk.util.BotRouter import *

class BotRoute:
    def __init__(self, bot, concurrentModule = None):
        self.bot = bot
        self.concurrentModule = concurrentModule
        self.pluginsManager = BotPluginsManager(self.bot)
        self.pluginsManager.init()
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]

    @asyncTraceBack
    @asyncTimeTest
    async def route(self, request : BotRequest):
        for i in range(len(self.router)):
            if (re := await self.router[i].route( \
                self.pluginsManager, request, self.concurrentModule)) \
                is not None and re is False:
                return
    
    def getPluginsManager(self):
        return self.pluginsManager