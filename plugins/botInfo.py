from botsdk.tool.BotPlugin import BotPlugin
from botsdk.BotRequest import BotRequest
from botsdk.tool.MessageChain import MessageChain

class plugin(BotPlugin):
    "来自XyzB0ts\n项目地址https://github.com/f88af65a/XyzB0ts"
    def __init__(self):
        super().__init__()
        self.name = "botInfo"
    
    def botinfo(self, request: BotRequest):
        request.sendMessage(MessageChain().plain("来自XyzB0ts\n项目地址https://github.com/f88af65a/XyzB0ts"))

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
