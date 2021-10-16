import botsdk.Bot
import botsdk.BotRequest
import botsdk.tool.JsonConfig
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.BotPlugin import BotPlugin

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.listenType = []
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenTarget = [["GroupMessage", "config", self.config], \
                ]
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.name = "systemHelp"
        #"插件名称"
        self.info = "管理系统的插件"
        #"插件信息"
        self.help = "/[config] [reload]"
        #"插件帮助"

    async def config(self, request):
        data = request.getFirstTextSplit()
        bot = request.bot
        route = request.route
        if len(data) < 2:
            await request.sendMessage(MessageChain().text("缺少参数"))
            return
        if data[1] == "reload":
            botsdk.tool.JsonConfig.reload()
            await request.sendMessage(MessageChain().text("重新加载完成"))

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
