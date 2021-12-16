import asyncio
import json
import os
import uuid

from botsdk.util.Error import printTraceBack


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
        self.config = None
        # listener
        self.listener = {}
        # generalList
        self.generalList = []

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
    def initBySystem(self, bot):
        try:
            self.initPluginConfig()
            self.init(bot)
        except Exception:
            self.clear()
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
    def init(self, bot):
        pass

    # 手动清理bot使用的资源
    def clear(self):
        pass

    def getName(self):
        return self.name

    def getFutureDict(self):
        return self.futures

    def getFutureByName(self, name):
        if name in self.getFutureDict():
            return self.futures[name]
        return None

    def addFuture(self, name, func):
        if name in self.futures:
            return None
        self.getFutureDict()[name] = asyncio.run_coroutine_threadsafe(
            func,
            asyncio.get_event_loop())

    def removeFuture(self, name):
        if name in self.futures:
            self.futures[name].cancel()
            del self.futures[name]
            return True
        return False

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