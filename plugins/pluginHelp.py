from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.JsonConfig import getConfig
from botsdk.util.Permission import permissionCheck


class plugin(BotPlugin):
    '''/[help/info/load/reload/unload] 插件名'''
    def onLoad(self):
        self.name = "pluginHelp"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "help", self.helper)
        self.addTarget("FriendMessage", "help", self.helper)
        self.addTarget("GroupMessage", "load", self.load)
        self.addTarget("GroupMessage", "reload", self.reload)
        self.addTarget("GroupMessage", "unload", self.unload)
        self.addTarget("GroupMessage", "plugins", self.plugins)
        self.addTarget("GroupMessage", "targets", self.targets)
        self.addTarget("GROUP:9", "help", self.helper)
        self.addTarget("GROUP:9", "load", self.load)
        self.addTarget("GROUP:9", "reload", self.reload)
        self.addTarget("GROUP:9", "unload", self.unload)
        self.addTarget("GROUP:9", "plugins", self.plugins)
        self.addTarget("GROUP:9", "targets", self.targets)

    async def helper(self, request):
        """help 命令名"""
        data = request.getFirstTextSplit()
        retMessage = self.helper.__doc__
        for i in range(1):
            if len(data) == 1:
                pluginManager = request.getPluginsManager()
                allName = pluginManager.getAllPluginName()
                ret = []
                for j in allName:
                    listener = pluginManager.getPlugin(j).getListener()
                    checkSet = set()
                    if request.getType() in listener:
                        for k in listener[request.getType()]["targetListener"]:
                            if (k in checkSet
                                    or not await permissionCheck(request, k)):
                                continue
                            ret.append("{}: {}".format(
                                k,
                                listener[request.getType()]
                                ["targetListener"][k].__doc__ if
                                listener[request.getType()]
                                ["targetListener"][k].__doc__ else "无"))
                            checkSet.add(k)
                retMessage = "可用命令:\n" + "\n".join(ret)
            elif len(data) == 2:
                if not await permissionCheck(request, data[1]):
                    retMessage = "权限限制"
                    break
                helpMessage = request.getPluginsManager().getTarget(
                    request.getType(), data[1])
                if helpMessage is None:
                    retMessage = "命令不存在"
                    break
                retMessage = helpMessage.__doc__
            else:
                retMessage = "过多的参数"
        await request.sendMessage(retMessage)

    async def load(self, request):
        '''load 插件名'''
        data = request.getFirstTextSplit()
        route = request.getPluginsManager()
        if len(data) < 2:
            await request.sendMessage(self.load.__doc__)
            return
        path = data[1]
        re = route.loadPlugin(getConfig()["pluginsPath"] + path)
        await request.sendMessage("加载成功" if re else "加载失败")

    async def reload(self, request):
        '''load 插件名'''
        data = request.getFirstTextSplit()
        route = request.getPluginsManager()
        if len(data) < 2:
            await request.sendMessage(self.reload.__doc__)
            return
        targetPlugin = data[1]
        allName = route.getAllPluginName()
        if targetPlugin not in allName:
            await request.sendMessage("插件不存在")
            return
        re = route.reLoadPlugin(targetPlugin)
        await request.sendMessage("加载成功" if re else "加载失败")

    async def unload(self, request):
        '''unload 插件名'''
        data = request.getFirstTextSplit()
        route = request.getPluginsManager()
        if len(data) < 2:
            await request.sendMessage(self.unload.__doc__)
            return
        targetPlugin = data[1]
        allName = route.getAllPluginName()
        if targetPlugin not in allName:
            await request.sendMessage("插件不存在")
            return
        route.unLoadPlugin(targetPlugin)
        await request.sendMessage("卸载成功")

    async def plugins(self, request):
        '''plugins #打印所有插件'''
        route = request.getPluginsManager()
        await request.sendMessage(str(route.getAllPluginName()))

    async def targets(self, request):
        '''targets #打印所有指令'''
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
