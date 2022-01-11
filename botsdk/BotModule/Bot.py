import json

from botsdk.util.Adapter import getAdapter
from botsdk.util.JsonConfig import getConfig
from botsdk.util.Tool import getAttrFromModule


def getBot(data):
    return getAttrFromModule(
                (getConfig()["botPath"]
                 + data[0]["botType"]).replace("/", ".") + ".Bot",
                data[0]["botType"] + "Bot")(*data)


class Bot:
    def __init__(self, data, botService=None):
        self.data = data
        self.botType = data["botType"]
        self.adapter = getAdapter(self.botType, data)
        self.botService = botService
        if "config" not in self.data:
            with (open(getConfig()["botPath"] + self.botType + "/adapter.json")
                  ) as config:
                self.data["config"] = json.loads(config.read())
        self.ownerRole = self.data["config"]["config"]["ownerRole"]
        self.init()

    def __del__(self):
        self.destroy()

    def setHandleModuleName(self, name):
        self.data["handleModuleName"] = name

    def getHandleModuleName(self):
        return self.data["handleModuleName"]

    def getConfig(self):
        return self.config

    def getOwnerRole(self):
        return self.ownerRole

    def getBotService(self):
        return self.botService

    def getData(self):
        return (self.data,)

    def getBotType(self):
        return self.botType

    def makeMessageChain(self, data=None):
        return getAttrFromModule(
            (getConfig()["botPath"]
             + self.data["botType"]).replace("/", ".")
            + ".MessageChain", self.data["botType"] + "MessageChain")(data)

    # needOverRide
    def init(self):
        pass

    def destroy(self):
        pass

    async def login(self):
        pass

    async def logout(self):
        pass

    async def onError(self, data):
        pass

    async def fetchMessage(self):
        pass
