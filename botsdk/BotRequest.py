from uuid import uuid4
from botsdk.tool.MessageType import messageType
from botsdk.tool.OutDated import OutDated

class BotRequest:
    def __init__(self, data, bot, route = None):
        self.bot = bot
        self.route = route
        self.type = data["type"]
        self.originData = data
        self.uuid = uuid4()
        if self.type in messageType:
            self.messageChain = data["messageChain"]
            self.sender = data["sender"]
            self.senderId = str(self.sender["id"])
            self.qq = str(self.sender["id"])
            if self.type == "GroupMessage":
                self.id = f"""{self.sender["id"]}:{self.sender["group"]["id"]}"""
                self.groupId = str(self.sender["group"]["id"])
                self.permission = self.sender["permission"]
                self.myPermission = self.sender["group"]["permission"]
            elif self.type == "FriendMessage":
                self.id = self.qq

    def __str__(self):
        stringList = []
        for i in self.messageChain:
            if i["type"] == "Plain":
                stringList.append(i["text"])
        return "".join(stringList)

    def getBot(self):
        return self.bot
    
    def getRoute(self):
        return self.route

    def getUuid(self):
        return self.uuid

    def getType(self):
        return self.type

    def getId(self):
        return self.id

    def getSenderId(self):
        return self.senderId

    def getGroupId(self):
        return self.groupId

    def getOriginData(self):
        return self.originData

    def getMessageChain(self):
        return self.messageChain

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
        return self.permission

    def getMyPermission(self):
        return self.myPermission

    async def sendMessage(self, msgChain):
        await self.bot.sendMessage(self.id, msgChain.getData())
