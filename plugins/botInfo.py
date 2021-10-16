from botsdk.tool.BotPlugin import BotPlugin

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "bot"
        self.info = "来自XyzB0ts\n项目地址https://github.com/f88af65a/XyzB0ts"
        self.help = ""

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
