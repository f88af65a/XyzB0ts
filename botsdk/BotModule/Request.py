from botsdk.util.BotException import BotException
from botsdk.util.Cookie import getCookie, setCookie
from botsdk.util.Tool import getAttrFromModule
from botsdk.util.JsonConfig import getConfig
from botsdk.BotModule.Bot import getBot


def getRequest(data):
    getAttrFromModule(
        (getConfig()["botPath"]
         + data["botType"].replace("/", ".")
         + ".Request"),
        data["bot"]["botType"] + "Request")(data)


class Request(dict):
    def __init__(self, data, responseChain, route=None):
        super().__init__(responseChain)
        self.data = data
        self.route = route
        self.bot = None

    def getBot(self):
        if self.bot is None:
            self.bot = getBot(*self.data["bot"])
        return self.bot

    def getData(self):
        return (self.data, dict(self))

    def getCookie(self, target: str = None):
        return getCookie(self.getId(), target)

    def setCookie(self, target: str, cookie):
        setCookie(self.getId(), target, cookie)

    def setHandleModuleName(self, name):
        self.data["handleModuleName"] = name

    def getHandleModuleName(self):
        return self.data["handleModuleName"]

    def setControlData(self, controlData):
        self.data["controlData"] = controlData

    def getControlData(self):
        return self.data["controlData"]

    def setTarget(self, target):
        self.data["target"] = target

    def getTarget(self):
        return self.data["target"]

    # needOverRide
    def getId(self):
        pass

    def getFirstText(self):
        pass

    def sendMessage(self, messageChain):
        pass

    def getType(self):
        pass

    # old

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

    def getMyQq(self):
        return self.data["qq"]

    def getFirst(self, messageType):
        for i in self.getMessageChain()[1:]:
            if i["type"] == messageType:
                return i
        return None

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
