from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Permission import permissionCheck


class plugin(BotPlugin):
    '''help [命令]'''
    def onLoad(self):
        self.name = "pluginHelp"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "help", self.helper)
        self.addTarget("FriendMessage", "help", self.helper)
        self.addTarget("Group:9", "help", self.helper)

    async def helper(self, request):
        """help [命令名]"""
        data = request.getFirstTextSplit()
        for i in range(1):
            if len(data) == 1:
                pluginManager = request.getPluginManager()
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
                helpMessage = request.getPluginManager().getTarget(
                    request.getType(), data[1])
                if helpMessage is None:
                    retMessage = "命令不存在"
                    break
                if helpMessage.__doc__ is None:
                    retMessage = "无提示信息"
                    break
                retMessage = helpMessage.__doc__
            else:
                retMessage = "过多的参数"
        await request.sendMessage(retMessage)


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
