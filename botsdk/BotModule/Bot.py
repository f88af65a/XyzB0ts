import json

from ..util.GetModule import getAdapter
from botsdk.util.JsonConfig import getConfig
from botsdk.util.Tool import getAttrFromModule


class Bot:
    def __init__(self, data, botService=None):
        self.data = data
        self.botType = data["botType"]
        self.adapter = getAdapter(data)
        self.botService = botService
        if "adapterConfig" not in self.data:
            with (open(getConfig()["botPath"] + self.botType + "/adapter.json")
                  ) as config:
                self.data["adapterConfig"] = json.loads(config.read())
        self.ownerRole = self.data["adapterConfig"]["config"]["ownerRole"]
        self.canDetach = True
        self.init()

    def __del__(self):
        self.destroy()

    def setTimer(self, timer):
        self.timer = timer

    def getTimer(self):
        return self.timer

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

    def getServiceType(self):
        return self.data["serviceType"]

    def makeMessageChain(self, data=None):
        return getAttrFromModule(
            (getConfig()["botPath"]
             + self.data["botType"]).replace("/", ".")
            + ".MessageChain", self.data["botType"] + "MessageChain")(data)

    def getCanDetach(self):
        return self.canDetach

    def getBotName(self):
        return self.data["botName"]

    # needOverRide
    # 初始化时调用
    def init(self):
        pass

    # 销毁时调用(未启用)
    def destroy(self):
        pass

    # 登录
    async def login(self):
        pass

    # 退出
    async def logout(self):
        pass

    # 获取消息
    # 返回值
    # (0成功/1异常，成功为消息列表/失败为返回的消息)
    async def fetchMessage(self):
        pass

    # 发送消息接口
    async def sendMessage(self, messageChain, request=None, id=None):
        pass

    # 路由前过滤 返回True则可以继续执行
    async def filter(self, request) -> bool:
        return True
