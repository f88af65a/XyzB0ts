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
        """/help 命令名"""
        data = request.getFirstTextSplit()
        if len(data) < 3:
            await request.sendMessage("缺少参数")
            return
        route = request.getPluginsManager()
        if (re := route.getTarget(request.getType(), data[2])) is not None:
            await request.sendMessage(re.__doc__)
        else:
            await request.sendMessage("不存在")

    async def load(self, request):
        data = request.getFirstTextSplit()
        route = request.getPluginsManager()
        if len(data) < 2:
            await request.sendMessage("缺少参数")
            return
        path = data[1]
        re = route.loadPlugin(getConfig()["pluginsPath"] + path)
        await request.sendMessage("加载成功" if re else "加载失败")

    async def reload(self, request):
        data = request.getFirstTextSplit()
        route = request.getPluginsManager()
        if len(data) < 2:
            await request.sendMessage("缺少参数")
            return
        targetPlugin = data[1]
        allName = route.getAllPluginName()
        if targetPlugin not in allName:
            await request.sendMessage("插件不存在")
            return
        re = route.reLoadPlugin(targetPlugin)
        await request.sendMessage("加载成功" if re else "加载失败")

    async def unload(self, request):
        data = request.getFirstTextSplit()
        route = request.getPluginsManager()
        if len(data) < 2:
            await request.sendMessage("缺少参数")
            return
        targetPlugin = data[1]
        allName = route.getAllPluginName()
        if targetPlugin not in allName:
            await request.sendGroupMessage("插件不存在")
            return
        route.unLoadPlugin(targetPlugin)
        await request.sendGroupMessage("卸载成功")

    async def plugins(self, request):
        route = request.getPluginsManager()
        await request.sendMessage(str(route.getAllPluginName()))

    async def targets(self, request):
        route = request.getPluginsManager()
        allName = route.getAllPluginName()
        re = []
        for i in allName:
            listener = route.getPlugin(i).getListener()
            for j in listener:
                for k in listener[j]["targetListener"]:
                    re.append("{}:{}".format(i, k))
        await request.sendMessage(str(re))


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
