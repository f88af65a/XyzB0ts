import asyncio
import copy

from botsdk.util.BotNotifyModule import getNotifyModule
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.ZookeeperTool import GetBotByName


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "test"
        self.addBotType("Mirai")
        self.canDetach = True

    def init(self):
        self.addLoopEvent(self.notifyTest)

    async def notifyTest(self):
        while True:
            await asyncio.sleep(10)
            notifyModule = getNotifyModule()
            notifySet = copy.deepcopy(notifyModule.notify("bot.notify.test"))
            for i in notifySet:
                botName = i.split(":")[0]
                bot = GetBotByName(botName)
                if bot is None:
                    continue
                dynamicChain = bot.makeMessageChain().text("hello")
                await bot.sendMessage(dynamicChain, id=i)


def handle():
    return plugin()
