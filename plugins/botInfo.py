from botsdk.tool.BotPlugin import BotPlugin

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "botInfo"
        self.info = "本项目来自XyzB0ts\n项目地址https://github.com/f88af65a/XyzB0ts"
        self.help = ""

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
