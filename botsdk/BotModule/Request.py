from botsdk.util.Cookie import getCookie, setCookie
from botsdk.util.Tool import getAttrFromModule
from botsdk.util.JsonConfig import getConfig
from botsdk.BotModule.Bot import getBot


def getRequest(data):
    return getAttrFromModule(
        ((getConfig()["botPath"]
         + data[0]["bot"][0]["botType"]).replace("/", ".")
         + ".Request"),
        data[0]["bot"][0]["botType"] + "Request")(*data)


class Request(dict):
    def __init__(self, data, responseChain, route=None):
        super().__init__(responseChain)
        self.data = data
        self.route = route
        self.bot = None
        self.init()

    def init(self):
        pass

    def getBot(self):
        if self.bot is None:
            self.bot = getBot(self.data["bot"])
        return self.bot

    def getRoute(self):
        return self.route

    def getPluginsManager(self):
        return self.route.getPluginsManager()

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

    def getUuid(self):
        return self.data["uuid"]

    def makeMessageChain(self, data=None):
        return self.getBot().makeMessageChain(data)

    def getFirstTextSplit(self):
        return self.getFirstText().split(" ")

    async def sendMessage(self, messageChain, request):
        await self.getBot().sendMessage(
            self.getId(), messageChain, request)

    # needOverRide
    # 获取角色
    def getRoles(self):
        pass

    # 获取发送者的BotId
    def getUserId(self):
        pass

    # 获取接收到数据的BotId
    def getId(self):
        pass

    # 获取消息的首个字符串
    def getFirstText(self):
        pass

    # 修改消息的首个字符串
    def setFirstText(self):
        pass

    # 获取消息类型
    def getType(self):
        pass

    def isSingle(self):
        pass
