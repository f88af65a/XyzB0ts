from botsdk.util.Adapter import getAdapter


class Bot:
    def __init__(self, data, botService=None):
        self.data = data
        self.botType = data["botType"]
        self.adapter = getAdapter(self.botType, data)
        self.botService = botService
        self.init()

    def __del__(self):
        self.destroy()

    def init(self):
        pass

    def destroy(self):
        pass

    def getBotService(self):
        return self.botService

    def getData(self):
        return (self.data)

    def getBotType(self):
        return self.botType

    async def login(self):
        pass

    async def logout(self):
        pass

    async def onError(self, data):
        pass

    async def fetchMessage(self):
        pass
