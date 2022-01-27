from threading import Thread
from multiprocessing import Queue
from botsdk.util.BotPlugin import BotPlugin
from discum import Client
from botsdk.util.BotNotifyModule import getNotifyModule


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "discord"
        self.addBotType("Mirai")
        self.queue = None
        self.stopQueue = None
        self.thread = None

    def init(self, bot):
        self.queue = Queue()
        self.stopQueue = Queue()
        self.thread = Thread(
            target=plugin.discordThreadFunc,
            args=(self.queue, self.stopQueue, self.getConfig()["token"]))
        self.thread.start()
        bot.getTimer().addTimer(
            plugin.checkQueue, [
                bot, self.queue,
                self.stopQueue, bot.getTimer()], 15)

    def onUnload(self):
        if self.queue is not None:
            self.queue.close()
        if self.thread is not None:
            self.stopQueue.append("stop")

    async def toNotify(notifyName, bot, messageChain):
        notifyModule = getNotifyModule()
        notifySet = notifyModule.notify(notifyName)
        for i in notifySet:
            if i.split(":")[0] == bot.getServiceType():
                await bot.sendMessage(i, messageChain)

    async def checkQueue(timerId, bot, queue, stopQueue, timer):
        if not stopQueue.empty():
            timer.delTimer(timerId)
        while not queue.empty():
            data = queue.get()
            plugin.toNotify(
                f"discord.{data[1]}.content", bot, bot.makeMessageChain().text(
                    f"{data[2]}:{data[4]}"))

    def discordThreadFunc(queue, stopQueue, token):
        bot = Client(token, log=False)

        @bot.gateway.command
        def fetchMessage(resp):
            if not stopQueue.empty():
                bot.gateway.close()
            if resp.event.ready_supplemental:
                user = bot.gateway.session.user
                print("Logged in as {}#{}".format(
                    user['username'], user['discriminator']))
            if resp.event.message:
                m = resp.parsed.auto()
                guildID = m['guild_id'] if 'guild_id' in m else None
                channelID = m['channel_id']
                username = m['author']['username']
                discriminator = m['author']['discriminator']
                content = m['content']
                queue.put(
                    [guildID, channelID, username, discriminator, content])
        bot.gateway.run(auto_reconnect=True)


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
