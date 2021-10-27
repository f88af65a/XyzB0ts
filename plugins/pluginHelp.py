import botsdk.Bot
import botsdk.BotRequest
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.BotPlugin import BotPlugin
class plugin(BotPlugin):
    '''/[help/info/load/reload/unload] 插件名'''
    def __init__(self):
        super().__init__()
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenTarget = [["GroupMessage", "help", self.helper], \
                             ["GroupMessage", "load", self.load], \
                             ["GroupMessage", "reload", self.reload], \
                             ["GroupMessage", "unload", self.unload], \
                             ["GroupMessage", "plugins", self.plugins], \
                             ["GroupMessage", "targets", self.targets], \
                ]
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.name = "pluginHelp"
        #"插件名称"

    async def helper(self, request):
        """/help [plugin/target] [插件名/命令名]"""
        data = request.getFirstTextSplit()
        if len(data) < 3:
            await request.sendMessage(MessageChain().text("缺少参数"))
            return
        route = request.getRoute()
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

    async def load(self, request):
        data = request.getFirstTextSplit()
        bot = request.getBot()
        route = request.getRoute()
        if len(data) < 2:
            await bot.sendGroupMessage(request.getGroupId(), MessageChain().text("缺少参数").getData())
            return
        path = data[1]
        re = route.loadPlugin(path)
        await bot.sendGroupMessage(request.getGroupId(), MessageChain().text("加载成功" if re else "加载失败").getData())

    async def reload(self, request):
        data = request.getFirstTextSplit()
        bot = request.getBot()
        route = request.getRoute()
        if len(data) < 2:
            await bot.sendGroupMessage(request.getGroupId(), MessageChain().text("缺少参数").getData())
            return
        targetPlugin = data[1]
        allName = route.getAllPluginName()
        if targetPlugin not in allName:
            await bot.sendGroupMessage(request.getGroupId(), MessageChain().text("插件不存在").getData())
            return
        re = route.reLoadPlugin(targetPlugin)
        await bot.sendGroupMessage(request.getGroupId(), MessageChain().text("加载成功" if re else "加载失败").getData())

    async def unload(self, request):
        data = request.getFirstTextSplit()
        bot = request.getBot()
        route = request.getRoute()
        if len(data) < 2:
            await bot.sendGroupMessage(request.getGroupId(), MessageChain().text("缺少参数").getData())
            return
        targetPlugin = data[1]
        allName = route.getAllPluginName()
        if targetPlugin not in allName:
            await bot.sendGroupMessage(request.getGroupId(), MessageChain().text("插件不存在").getData())
            return
        request.route.unLoadPlugin(targetPlugin)
        await bot.sendGroupMessage(request.getGroupId(), MessageChain().text("卸载成功").getData())

    async def plugins(self, request):
        bot = request.getBot()
        route = request.getRoute()
        await bot.sendGroupMessage(request.getGroupId(), MessageChain().text(str(route.getAllPluginName())).getData())

    async def targets(self, request):
        bot = request.getBot()
        route = request.getRoute()
        allName = route.getAllPluginName()
        re = []
        for i in allName:
            for j in route.getPlugin(i).getListenTarget():
                re.append("{}:{}".format(i, j[1]))
        await bot.sendGroupMessage(request.getGroupId(), MessageChain().text(str(re)).getData())

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
