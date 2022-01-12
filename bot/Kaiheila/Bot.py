from botsdk.BotModule.Bot import Bot


class KaiheilaBot(Bot):
    # needOverRide
    def init(self):
        self.canDetach = False

    async def getGateway(self):
        return await self.adapter.getGateway()

    def destroy(self):
        pass

    async def login(self):
        self.gateway = await self.getGateway()
        print(self.gateway)

    async def logout(self):
        pass

    async def fetchMessage(self):
        pass
