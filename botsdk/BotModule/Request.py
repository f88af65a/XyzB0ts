from botsdk.util.Cookie import getCookie, setCookie
from ..util.GetModule import getBot
from ..util.RunInThread import asyncRunInThread


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

    def getCookie(self, target: str = None, id=None):
        if "cookie" not in self.data:
            self.data["cookie"] = getCookie(self.getId())
        if id is None:
            if target is None:
                return self.data["cookie"]
            if target in self.data["cookie"]:
                return self.data["cookie"][target]
            return None
        return getCookie(id, target)

    def setCookie(self, target: str, cookie, id=None):
        if "cookie" in self.data and id is None:
            self.data["cookie"][target] = cookie
        setCookie(id if id else self.getId(), target, cookie)

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

    async def sendMessage(self, messageChain, id=None):
        asyncRunInThread(
            self.getBot().sendMessage,
            messageChain,
            request=self,
            id=id
            )

    async def syncSendMessage(self, messageChain, *args, **kwargs):
        await self.getBot().sendMessage(
            messageChain,
            self,
            *args, **kwargs
            )

    def userFormat(self, userId):
        return self.getBot().userFormat(userId)

    def groupFormat(self, groupId):
        return self.getBot().groupFormat(userId)

    # needOverRide
    # 获取请求数据中的角色
    def getRoles(self):
        pass

    # 获取发送者的BotId
    # 可能返回None(
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

    def isMessage(self):
        pass
