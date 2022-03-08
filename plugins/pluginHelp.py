from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.JsonConfig import getConfig
from botsdk.util.Permission import permissionCheck, listPermissionCheck


class plugin(BotPlugin):
    '''/[help/info/load/reload/unload] 插件名'''
    def onLoad(self):
        self.name = "pluginHelp"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
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
        """help 命令名"""
        data = request.getFirstTextSplit()
        if len(data) == 1:
            route = request.getPluginsManager()
            allName = route.getAllPluginName()
            ret = []
            checkSet = set()
            for i in allName:
                listener = route.getPlugin(i).getListener()
                for j in listener:
                    for k in listener[j]["targetListener"]:
                        checkSet.add([k, listener[j]["targetListener"][k]])
            targetList = list(checkSet)
            permissionCheckList = listPermissionCheck(
                request, [i[0] for i in targetList])
            ret = []
            for i in range(len(targetList)):
                if permissionCheckList[i]:
                    ret.append("{}: {}".format(
                        targetList[i][0],
                        targetList[i][1].__doc__ if targetList[i][1].__doc__
                        else "无"))
            await request.sendMessage("可用命令:\n" + "\n".join(ret))
        elif len(data) == 2:
            if await permissionCheck(request, data[1]):
                route = request.getPluginsManager()
                if ((re := route.getTarget(request.getType(), data[1]))
                        is not None):
                    await request.sendMessage(re.__doc__)
                else:
                    await request.sendMessage("命令不存在")
            else:
                await request.sendMessage("权限限制")
        else:
            await request.sendMessage("???")

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
            await request.sendGroupMessage("插件不存在")
            return
        route.unLoadPlugin(targetPlugin)
        await request.sendGroupMessage("卸载成功")

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
