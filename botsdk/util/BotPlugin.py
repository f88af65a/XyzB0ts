import os
import uuid

import ujson as json

from .Error import printTraceBack


class BotPlugin:
    def __init__(self):
        self.name = ""
        # 插件所定义的任务
        self.futures = dict()
        # 是否可以分离到线程中安全执行
        self.canDetach = False
        # UUID
        self.uuid = uuid.uuid4()
        # 配置文件,在pluginInit中初始化
        self.config = {}
        # listenerk
        self.listener = {}
        # generalList
        self.generalList = []
        # 兼容的bot类型
        self.botSet = set()
        # Loop 会在router中执行
        self.loopEvent = []

    def getBotSet(self):
        return self.botSet

    def addBotType(self, botType: str):
        self.botSet.add(botType)

    def addType(self, typeName: str, func):
        if typeName not in self.getListener():
            self.getListener()[typeName] = {"typeListener": set(),
                                            "targetListener": dict()}
        self.getListener()[typeName]["typeListener"].add(func)

    def addTarget(self, typeName: str, targetName: str, func):
        if typeName not in self.getListener():
            self.getListener()[typeName] = {"typeListener": set(),
                                            "targetListener": dict()}
        self.getListener()[typeName]["targetListener"][targetName] = func

    def addGeneral(self, priority, func):
        self.getGeneralList().append((priority, func))

    def addFilter(self, func):
        self.addGeneral(5, func)

    def addFormat(self, func):
        self.addGeneral(6, func)

    # 系统调用的初始化函数
    def initBySystem(self):
        try:
            self.initPluginConfig()
            self.init()
        except Exception:
            printTraceBack()
            return False
        return True

    # 配置文件初始化
    def initPluginConfig(self):
        pluginConfigPath = f'''./configs/{self.name}/config.json'''
        if os.path.exists(pluginConfigPath):
            with open(pluginConfigPath, "r") as configFile:
                self.config = json.loads(configFile.read())

    # 在成功加载后才会调用
    def init(self):
        pass

    # 加载时调用
    def onLoad(self):
        pass

    # 卸载时调用
    def onUnload(self):
        pass

    def getName(self):
        return self.name

    def addLoopEvent(self, c, *args, **kwargs):
        self.loopEvent.append([c, args, kwargs])

    def getLoopEvent(self):
        return self.loopEvent

    def getCanDetach(self):
        return self.canDetach

    def getUuid(self):
        return self.uuid

    def getConfig(self):
        return self.config

    def getListener(self):
        return self.listener

    def getGeneralList(self):
        return self.generalList
