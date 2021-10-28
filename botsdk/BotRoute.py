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
        self.pluginManage = BotPluginsManager()
        self.router = [FilterAndFormatRouter(), TypeRouter(), TargetRouter()]

    @asyncExceptTrace
    @asyncTimeTest
    async def route(self, request : BotRequest):
        for i in range(len(self.router)):
            if not await self.router[i].route(self, self.pluginManage, request):
                return
    
    def getPluginsManage(self):
        return self.getPluginsManage