from botsdk.Bot import Bot

class BotRequest(dict):
    def __init__(self, data, responseChain, route = None):
        '''
        BotRquest(dict)
        继承自dict，封装了部分处理消息的函数
        '''
        super().__init__(responseChain)
        self.route = route
        self.data=data
    
    #Route辅助函数
    def getBot(self):
        return Bot(*self.data["bot"])
    
    def getRoute(self):
        return self.route
    
    def getPluginsManager(self):
        return self.route.getPluginsManager()

    def getUuid(self):
        return self.data["uuid"]

    def getMessageId(self):
        return self["messageChain"][0]["id"]
    
    def getMessageTime(self):
        return self["messageChain"][0]["time"]

    def getData(self):
        return (self.data, dict(self))

    def setControlData(self, controlData):
        self.data["controlData"] = controlData
    
    def getControlData(self):
        return self.data["controlData"]

    def setTarget(self, target):
        self.data["target"] = target

    def getTarget(self):
        return self.data["target"]
    
    def setPluginPath(self, path):
        self.data["pluginPath"] = path
    
    def getPluginPath(self):
        return self.data["pluginPath"]
    
    def getMyQq(self):
        return self.data["qq"]

    #消息辅助函数
    def getType(self):
        return self["type"]

    def getId(self):
        if self["type"] == "GroupMessage":
            return f"""{self["sender"]["id"]}:{self["sender"]["group"]["id"]}"""
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

    async def sendMessage(self, msgChain, quote = None):
        await self.getBot().sendMessage(self.getId(), msgChain.getData(), quote)