from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.JsonConfig import getConfig


class plugin(BotPlugin):
    '''/[help/info/load/reload/unload] 插件名'''
    def onLoad(self):
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.name = "pluginHelp"
        self.addTarget("GroupMessage", "help", self.helper)
        self.addTarget("GroupMessage", "load", self.load)
        self.addTarget("GroupMessage", "reload", self.reload)
        self.addTarget("GroupMessage", "unload", self.unload)
        self.addTarget("GroupMessage", "plugins", self.plugins)
        self.addTarget("GroupMessage", "targets", self.targets)
        self.addTarget("GROUP:1", "help", self.helper)
        self.addTarget("GROUP:1", "load", self.load)
        self.addTarget("GROUP:1", "reload", self.reload)
        self.addTarget("GROUP:1", "unload", self.unload)
        self.addTarget("GROUP:1", "plugins", self.plugins)
        self.addTarget("GROUP:1", "targets", self.targets)

    async def helper(self, request):
        """/help [plugin/target] [插件名/命令名]"""
        data = request.getFirstTextSplit()
        if len(data) < 3:
            await request.sendMessage("缺少参数")
            return
        route = request.getPluginsManager()
        if data[1] == "plugin":
            if (re := route.getPlugin(data[2])) is not None:
                await request.sendMessage(re.__doc__)
                return
        elif data[1] == "target":
            if (re := route.getTarget(request.getType(), data[2])) is not None:
                await request.sendMessage(re.__doc__)
                return
        else:
            await request.sendMessage("参数错误")
            return
        await request.sendMessage("不存在")

    async def load(self, request):
        data = request.getFirstTextSplit()
        bot = request.getBot()
        route = request.getPluginsManager()
        if len(data) < 2:
            await bot.sendGroupMessage(
                request.getGroupId(),
                request.makeMessageChain().text("缺少参数").getData())
            return
        path = data[1]
        re = route.loadPlugin(getConfig()["pluginsPath"] + path)
        await bot.sendGroupMessage(
            request.getGroupId(),
            request.makeMessageChain()
            .text("加载成功" if re else "加载失败").getData())

    async def reload(self, request):
        data = request.getFirstTextSplit()
        bot = request.getBot()
        route = request.getPluginsManager()
        if len(data) < 2:
            await bot.sendGroupMessage(
                request.getGroupId(),
                request.makeMessageChain().text("缺少参数").getData())
            return
        targetPlugin = data[1]
        allName = route.getAllPluginName()
        if targetPlugin not in allName:
            await bot.sendGroupMessage(
                request.getGroupId(),
                request.makeMessageChain().text("插件不存在").getData())
            return
        re = route.reLoadPlugin(targetPlugin)
        await bot.sendGroupMessage(
            request.getGroupId(),
            request.makeMessageChain()
            .text("加载成功" if re else "加载失败").getData())

    async def unload(self, request):
        data = request.getFirstTextSplit()
        bot = request.getBot()
        route = request.getPluginsManager()
        if len(data) < 2:
            await bot.sendGroupMessage(
                request.getGroupId(),
                request.makeMessageChain().text("缺少参数").getData())
            return
        targetPlugin = data[1]
        allName = route.getAllPluginName()
        if targetPlugin not in allName:
            await bot.sendGroupMessage(
                request.getGroupId(),
                request.makeMessageChain().text("插件不存在").getData())
            return
        route.unLoadPlugin(targetPlugin)
        await bot.sendGroupMessage(
            request.getGroupId(),
            request.makeMessageChain().text("卸载成功").getData())

    async def plugins(self, request):
        bot = request.getBot()
        route = request.getPluginsManager()
        await bot.sendGroupMessage(
            request.getGroupId(),
            request.makeMessageChain()
            .text(str(route.getAllPluginName())).getData())

    async def targets(self, request):
        bot = request.getBot()
        route = request.getPluginsManager()
        allName = route.getAllPluginName()
        re = []
        for i in allName:
            listener = route.getPlugin(i).getListener()
            for j in listener:
                for k in listener[j]["targetListener"]:
                    re.append("{}:{}".format(i, k))
        await bot.sendGroupMessage(
            request.getGroupId(),
            request.makeMessageChain().text(str(re)).getData())


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
