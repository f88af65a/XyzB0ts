import random
from botsdk.util.BotPlugin import BotPlugin
from botsdk.BotRequest import BotRequest
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.MessageChain import MessageChain

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "random"
        self.addTarget("GroupMessage", "random", self.random)
    
    def random(self, request: BotRequest):
        "/random 最小值 最大值"
        data = request.getFirstTextSplit()
        if len(data) < 3:
            request.sendMessage(MessageChain().plain(self.random.__doc__))
            return
        try:
            l, r = int(data[1]), int(data[2])
            if l > r:
                raise
        except Exception:
            request.sendMessage(MessageChain().plain(self.random.__doc__))
        request.sendMessage(MessageChain().plain(str(random.randint(l, r))))