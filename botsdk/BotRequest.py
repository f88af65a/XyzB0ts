from botsdk.Bot import Bot
from botsdk.util.BotException import BotException
from botsdk.util.Cookie import getCookie
from botsdk.util.Cookie import setCookie
from botsdk.util.MessageChain import MessageChain

class BotRequest(dict):
    def __init__(self, data, responseChain, route = None):
        super().__init__(responseChain)
        self.data=data
        self.route = route
        self.bot = None
    
    def getBot(self):
        if self.bot is None:
            self.bot = Bot(*self.data["bot"])
        return self.bot
    
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
    
    def setHandleModuleName(self, name):
        self.data["handleModuleName"] = name
    
    def getHandleModuleName(self):
        return self.data["handleModuleName"]

    def getMyQq(self):
        return self.data["qq"]

    #消息辅助函数
    def getType(self):
        return self["type"]

    def getId(self):
        if self["type"] == "GroupMessage":
            return f"""Group:{self["sender"]["group"]["id"]}"""
        else:
            return f'''User:{self["sender"]["id"]}'''

    def getCookie(self, target: str=None):
        return getCookie(self.getId(), target)

    def setCookie(self, target: str, cookie):
        setCookie(self.getId(), target, cookie)

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

    async def sendMessage(self, msgChain:MessageChain , quote = None):
        if self.getType() == "FriendMessage":
            await self.getBot().sendFriendMessage(int(self.getSenderId()) \
                , msgChain.getData(), quote),
        elif self.getType() == "GroupMessage":
            await self.getBot().sendGroupMessage(int(self.getGroupId()) \
                , msgChain.getData(), quote),
        elif self.getType() == "TempMessage":
            await self.getBot().sendTempMessage(int(self.getGroupId()) \
                , int(self.getSenderId()), msgChain.getData(), quote)
    
    async def sendNudge(self, target):
        nudgeType = None
        if self["type"] == "GroupMessage":
            nudgeType = "Group"
        elif self["type"] == "FriendMessage":
            nudgeType = "Friend"
        else:
            raise BotException("sendNudge遇到了错误的消息类型")
        self.getBot().sendNudge(int(self.getBot().getQq()), int(target), nudgeType)
    
    async def recall(self, target):
        self.getBot().recall(int(target))