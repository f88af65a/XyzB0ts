import botsdk.Bot
import botsdk.BotRequest
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.BotPlugin import BotPlugin
class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.listenType = []
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenTarget = [["GroupMessage", "help", self.helpr], \
                             ["GroupMessage", "info", self.info], \
                             ["GroupMessage", "load", self.load], \
                             ["GroupMessage", "reload", self.reload], \
                             ["GroupMessage", "unload", self.unload], \
                             ["GroupMessage", "plugins", self.plugins], \
                             ["GroupMessage", "targets", self.targets], \
                ]
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.name = "pluginHelp"
        #"插件名称"
        self.info = "管理插件的插件"
        #"插件信息"
        self.help = "/[help/info/load/reload/unload] 插件名"
        #"插件帮助"

    async def helpr(self, request):
        data = request.getFirstTextSplit()
        bot = request.bot
        route = request.route
        if len(data) < 2:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("缺少参数").getData())
            return
        targetPlugin = data[1]
        allName = request.route.getAllPluginName()
        if targetPlugin not in allName:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("插件不存在").getData())
            return
        await bot.sendGroupMessage(request.groupId, MessageChain().text(route.getPlugin(targetPlugin).getHelp()).getData())

    async def info(self, request):
        data = request.getFirstTextSplit()
        bot = request.bot
        route = request.route
        if len(data) < 2:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("缺少参数").getData())
            return
        targetPlugin = data[1]
        allName = request.route.getAllPluginName()
        if targetPlugin not in allName:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("插件不存在").getData())
            return
        await bot.sendGroupMessage(request.groupId, MessageChain().text(route.getPlugin(targetPlugin).getInfo()).getData())

    async def load(self, request):
        data = request.getFirstTextSplit()
        bot = request.bot
        if len(data) < 2:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("缺少参数").getData())
            return
        path = data[1]
        re = request.route.loadPlugin(path)
        await bot.sendGroupMessage(request.groupId, MessageChain().text("加载成功" if re else "加载失败").getData())

    async def reload(self, request):
        data = request.getFirstTextSplit()
        bot = request.bot
        if len(data) < 2:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("缺少参数").getData())
            return
        targetPlugin = data[1]
        allName = request.route.getAllPluginName()
        if targetPlugin not in allName:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("插件不存在").getData())
            return
        re = request.route.reLoadPlugin(targetPlugin)
        await bot.sendGroupMessage(request.groupId, MessageChain().text("加载成功" if re else "加载失败").getData())

    async def unload(self, request):
        data = request.getFirstTextSplit()
        bot = request.bot
        if len(data) < 2:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("缺少参数").getData())
            return
        targetPlugin = data[1]
        allName = request.route.getAllPluginName()
        if targetPlugin not in allName:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("插件不存在").getData())
            return
        request.route.unLoadPlugin(targetPlugin)
        await bot.sendGroupMessage(request.groupId, MessageChain().text("卸载成功").getData())

    async def plugins(self, request):
        bot = request.bot
        await bot.sendGroupMessage(request.groupId, MessageChain().text(str(request.route.getAllPluginName())).getData())

    async def targets(self, request):
        bot = request.bot
        route = request.route
        allName = route.getAllPluginName()
        re = []
        for i in allName:
            for j in route.getPlugin(i).getListenTarget():
                re.append("{}:{}".format(i, j[1]))
        await bot.sendGroupMessage(request.groupId, MessageChain().text(str(re)).getData())


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
