from botsdk.BotRequest import BotRequest
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.MessageChain import MessageChain


class plugin(BotPlugin):
    '''/[help/info/load/reload/unload] 插件名'''
    def __init__(self):
        super().__init__()
        self.name = "pluginHelp"
        self.addTarget("GroupMessage", "help", self.helper)
        self.addTarget("GroupMessage", "load", self.load)
        self.addTarget("GroupMessage", "reload", self.reload)
        self.addTarget("GroupMessage", "unload", self.unload)
        self.addTarget("GroupMessage", "plugins", self.plugins)
        self.addTarget("GroupMessage", "targets", self.targets)

    async def helper(self, request: BotRequest):
        """/help [plugin/target] [插件名/命令名]"""
        data = request.getFirstTextSplit()
        if len(data) < 3:
            await request.sendMessage(MessageChain().text("缺少参数"))
            return
        route = request.getPluginsManager()
        if data[1] == "plugin":
            if (re := route.getPlugin(data[2])) is not None:
                await request.sendMessage(MessageChain().text(re.__doc__))
                return
        elif data[1] == "target":
            if (re := route.getTarget(request.getType(), data[2])) is not None:
                await request.sendMessage(MessageChain().text(re.__doc__))
                return
        else:
            await request.sendMessage(MessageChain().text("参数错误"))
            return
        await request.sendMessage(MessageChain().text("不存在"))

    async def load(self, request: BotRequest):
        data = request.getFirstTextSplit()
        bot = request.getBot()
        route = request.getPluginsManager()
        if len(data) < 2:
            await bot.sendGroupMessage(
                request.getGroupId(),
                MessageChain().text("缺少参数").getData())
            return
        path = data[1]
        re = route.loadPlugin(path)
        await bot.sendGroupMessage(
            request.getGroupId(),
            MessageChain().text("加载成功" if re else "加载失败").getData())

    async def reload(self, request: BotRequest):
        data = request.getFirstTextSplit()
        bot = request.getBot()
        route = request.getPluginsManager()
        if len(data) < 2:
            await bot.sendGroupMessage(
                request.getGroupId(),
                MessageChain().text("缺少参数").getData())
            return
        targetPlugin = data[1]
        allName = route.getAllPluginName()
        if targetPlugin not in allName:
            await bot.sendGroupMessage(
                request.getGroupId(),
                MessageChain().text("插件不存在").getData())
            return
        re = route.reLoadPlugin(targetPlugin)
        await bot.sendGroupMessage(
            request.getGroupId(),
            MessageChain().text("加载成功" if re else "加载失败").getData())

    async def unload(self, request: BotRequest):
        data = request.getFirstTextSplit()
        bot = request.getBot()
        route = request.getPluginsManager()
        if len(data) < 2:
            await bot.sendGroupMessage(
                request.getGroupId(),
                MessageChain().text("缺少参数").getData())
            return
        targetPlugin = data[1]
        allName = route.getAllPluginName()
        if targetPlugin not in allName:
            await bot.sendGroupMessage(
                request.getGroupId(),
                MessageChain().text("插件不存在").getData())
            return
        route.unLoadPlugin(targetPlugin)
        await bot.sendGroupMessage(
            request.getGroupId(),
            MessageChain().text("卸载成功").getData())

    async def plugins(self, request: BotRequest):
        bot = request.getBot()
        route = request.getPluginsManager()
        await bot.sendGroupMessage(
            request.getGroupId(),
            MessageChain().text(str(route.getAllPluginName())).getData())

    async def targets(self, request: BotRequest):
        bot = request.getBot()
        route = request.getPluginsManager()
        allName = route.getAllPluginName()
        re = []
        for i in allName:
            for j in route.getPlugin(i).getListenTarget():
                re.append("{}:{}".format(i, j[1]))
        await bot.sendGroupMessage(
            request.getGroupId(),
            MessageChain().text(str(re)).getData())


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
