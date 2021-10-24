from uuid import uuid4
from botsdk.tool.MessageType import messageType
from botsdk.tool.OutDated import OutDated
from botsdk.Bot import Bot

class BotRequest(dict):
    def __init__(self, botData, responseChain, route = None):
        '''
        BotRquest(dict)
        继承自dict，封装了部分处理消息的函数
        '''
        super().__init__(responseChain)
        self.route = route
        self.data = {}
        self.data["uuid"] = uuid4()
        self.data["bot"] = botData
    
    def getBot(self):
        return Bot(self.data["bot"])
    
    def getRoute(self):
        return self.route

    def getUuid(self):
        return self.data["uuid"]

    def getType(self):
        return self["type"]

    def getId(self):
        if self["type"] == "GroupMessage":
            return f"""{self.sender["id"]}:{self.sender["group"]["id"]}"""
        elif self["type"] == "FriendMessage":
            return str(self["sender"]["id"])
        return None

    def getSenderId(self):
        return str(self["sender"]["id"])

    def getGroupId(self):
        return str(self["sender"]["group"]["id"])

    def getMessageChain(self):
        return self["messageChain"]

    def getFirst(self, messageType):
        for i in self.getMessageChain()[1:]:
            if i["type"] == messageType:
                return i
        return None

    def getFirstTextSplit(self):
        if (re := self.getFirst("Plain")) != None:
            return re["text"].split(" ")
        return None

    def getPermission(self):
        return self["sender"]["permission"]

    def getMyPermission(self):
        return self["sender"]["group"]["permission"]

    async def sendMessage(self, msgChain):
        await self.bot.sendMessage(self.id, msgChain.getData())

    #dev-BotRequestUpdate

    def getData(self):
        return (self.data, dict(self))

    def setControlData(self, controlData):
        self.data["controlData"] = controlData
    
    def getControlData(self):
        return self.data["controlData"]

    def setTarget(self, target):
        self.data["target"] = target

    def getTarget(self):
        return self["data"]["target"]
    
    def setPluginPath(self, path):
        self.data["pluginPath"] = path
    
    def getPluginPath(self, path):
        return self.data["pluginPath"]