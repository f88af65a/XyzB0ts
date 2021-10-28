from botsdk.tool.Error import *
from botsdk.tool.JsonConfig import getConfig
from botsdk.tool.TimeTest import asyncTimeTest
from botsdk.BotRequest import BotRequest
from botsdk.tool.BotPluginsManager import BotPluginsManager
from botsdk.tool.BotRouter import *

class BotRoute:
    def __init__(self, bot, concurrentModule = None):
        self.bot = bot
        self.concurrentModule = concurrentModule
        self.pluginsManager = BotPluginsManager(self.bot)
        self.pluginsManager.init()
        self.router = [FilterAndFormatRouter(), TypeRouter(), TargetRouter()]

    @asyncExceptTrace
    @asyncTimeTest
    async def route(self, request : BotRequest):
        for i in range(len(self.router)):
            if (re := await self.router[i].route( \
                self.pluginsManager, request, self.concurrentModule)) \
                is not None and re is False:
                return
    
    def getPluginsManager(self):
        return self.pluginsManager