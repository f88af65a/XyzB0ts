from botsdk.util.BotException import BotException
from botsdk.BotModule.Request import Request


class MiraiRequest(Request):
    def init(self):
        self.messageType = {
            "FriendMessage",
            "GroupMessage",
            "TempMessage",
            "StrangerMessage",
            "OtherClientMessage"
        }
        self.signalMessage = {
            "FriendMessage",
            "NewFriendRequestEvent",
            "BotInvitedJoinGroupRequestEvent"
        }

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

    # 消息辅助函数
    def getType(self):
        return self["type"]

    # 返回格式BotName:平台:类型:ID
    def getId(self):
        msgType = self.getType()
        if (msgType == "GroupMessage"
                or msgType == "TempMessage"):
            return (
                self.getBot().getBotName()
                + ":"
                + self.groupFormat(self["sender"]["group"]["id"])
                )
        elif msgType == "MemberJoinEvent":
            return (
                self.getBot().getBotName()
                + ":"
                + self.groupFormat(self["member"]["group"]["id"])
                )
        else:
            return (
                self.getBot().getBotName()
                + ":"
                + self.getUserId()
                )

    def getGroupId(self):
        return str(self["sender"]["group"]["id"])

    def getMessageChain(self):
        if self.getType() in self.messageType:
            return self["messageChain"]
        return None

    def getFirst(self, messageType):
        if self.getType() in self.messageType:
            for i in self.getMessageChain()[1:]:
                if i["type"] == messageType:
                    return i
        return None

    def getFirstText(self):
        if (re := self.getFirst("Plain")) is not None:
            return re["text"]
        return None

    def setFirstText(self, s):
        if (re := self.getFirst("Plain")) is not None:
            re["text"] = s

    def getFirstTextSplit(self):
        if (re := self.getFirst("Plain")) is not None:
            return re["text"].split(" ")
        return None

    def getPermission(self):
        return self["sender"]["permission"]

    def getMyPermission(self):
        return self["sender"]["group"]["permission"]

    async def sendNudge(self, target):
        nudgeType = None
        if self["type"] == "GroupMessage":
            nudgeType = "Group"
        elif self["type"] == "FriendMessage":
            nudgeType = "Friend"
        else:
            raise BotException("sendNudge遇到了错误的消息类型")
        self.getBot().sendNudge(
            int(self.getBot().getQq()), int(target), nudgeType)

    async def recall(self, target):
        self.getBot().recall(int(target))

    async def getRoles(self):
        ret = set()
        if "sender" in self and "permission" in self["sender"]:
            ret |= {self["sender"]["permission"]}
        return ret

    # 返回格式平台:类型:ID
    def getUserId(self):
        userId = None
        msgType = self.getType()
        if (msgType == "NewFriendRequestEvent"
                or msgType == "BotInvitedJoinGroupRequestEvent"):
            userId = self["fromId"]
        else:
            try:
                userId = self["sender"]["id"]
            except Exception:
                return None
        return self.userFormat(str(userId))

    def isSingle(self):
        return self.getType() in self.signalMessage

    def isMessage(self):
        return self.getType() in self.messageType

    async def isGroupOwner(self):
        return "OWNER" in await self.getRoles()
