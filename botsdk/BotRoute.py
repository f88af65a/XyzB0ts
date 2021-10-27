from botsdk.tool.Error import *
from botsdk.tool.JsonConfig import getConfig
from botsdk.tool.TimeTest import asyncTimeTest
from botsdk.BotRequest import BotRequest
from botsdk.tool.BotPluginsManager import BotPluginsManager
from botsdk.tool.BotRouter import *

class BotRoute:
    def __init__(self, bot, concurrentModule = None):
        self.bot = bot
        #插件目录路径
        self.pluginsPath = getConfig()["pluginsPath"]
        #{插件名:插件实例}
        self.plugins = dict()
        #{pluginName:pluginFileName}
        self.pluginPath = dict()
        #{messageType:{target:func}}
        self.targetRoute = dict()
        #{messageType:{func}}
        self.typeRoute = dict()
        #{func}
        self.filterSet = set()
        #{func}
        self.formatSet = set()
        self.concurrentModule = concurrentModule
        self.pluginManage = BotPluginsManager()
        self.router = [FilterAndFormatRouter(), TypeRouter(), TargetRouter()]

    @asyncExceptTrace
    @asyncTimeTest
    async def route(self, request : BotRequest):
        for i in range(len(self.router)):
            if not await self.router[i].route(self, self.pluginManage, request):
                return