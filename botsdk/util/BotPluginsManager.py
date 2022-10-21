import importlib
import os

from .Error import debugPrint, printTraceBack
from .JsonConfig import getConfig


class BotPluginsManager:
    def __init__(self):
        # 插件路径
        self.pluginsPath = getConfig()["pluginsPath"]
        # {插件名: 插件对象}
        self.plugins = dict()
        # {消息类型:{"typeListener":{func...}, "targetListener":{target:func...}}}
        self.listener = dict()
        # [(优先级,函数)]
        self.generalList = list()
        # 初始化
        self.loadAllPlugin()

    def __del__(self):
        for i in [i for i in self.plugins]:
            self.unLoadPlugin(i)

    def loadAllPlugin(self):
        for i in os.listdir(self.pluginsPath):
            if (os.path.isfile(f"{self.pluginsPath}{i}")
                    and self.loadPlugin(f"{self.pluginsPath}{i}")):
                debugPrint(f"插件{self.pluginsPath}{i}加载成功")

    def reLoadPlugin(self, pluginName: str):
        if pluginName in self.plugins:
            moduleName = self.plugins[pluginName].__module__
            self.unLoadPlugin(pluginName)
            return self.loadPlugin(moduleName)

    def loadPlugin(self, path: str):
        '''
        插件加载流程
        onload -> initBySystem -> initPluginConfig -> init
        '''
        path = path.replace("/", ".")
        if path[-3:] == ".py":
            path = path[:-3]
        # 加载
        try:
            module = importlib.reload(importlib.import_module(path))
            handle = getattr(module, "handle")()
        except Exception:
            printTraceBack()
            return False
        handle.onLoad()
        '''
        检查改为在插件中检查
        # 检查是否是兼容的
        if self.getBot().getBotType() not in handle.getBotSet():
            return False
        '''
        # 检查名称是否重复
        if handle.getName() in self.plugins:
            return False
        # 检查target是否重复
        handleListener = handle.getListener()
        for i in handleListener:
            for j in handleListener[i]:
                if (i in self.getListener()
                        and j in self.getListener()[i]["targetListener"]):
                    debugPrint(f"插件{handle.getName()} 类型{i}中使用了相同的target {j}")
                    return False
        # 系统初始化
        if not handle.initBySystem():
            return False
        # 添加信息
        for i in handleListener:
            if i not in self.listener:
                self.listener[i] = {"typeListener": set(),
                                    "targetListener": dict()}
            self.listener[i]["typeListener"] |= (
                handleListener[i]["typeListener"])
            self.listener[i]["targetListener"] |= (
                handleListener[i]["targetListener"])
        self.generalList += handle.getGeneralList()
        self.generalList.sort(key=lambda i: i[0])
        self.plugins[handle.getName()] = handle
        return True

    def unLoadPlugin(self, pluginName: str):
        if (re := self.getPlugin(pluginName)) is not None:
            for i in re.getListener():
                for j in re.getListener()[i]["typeListener"]:
                    if (i in self.listener
                            and j in self.listener[i]["typeListener"]):
                        self.listener[i]["typeListener"].remove(j)
                for j in re.getListener()[i]["targetListener"]:
                    if (i in self.listener
                            and j in self.listener[i]["targetListener"]):
                        del self.listener[i]["targetListener"][j]
            for i in re.getGeneralList():
                self.generalList.remove(i)
            self.plugins[pluginName].onUnload()
            del self.plugins[pluginName]

    def getListener(self):
        return self.listener

    def setListener(self, listener):
        self.listener = listener

    def getGeneralList(self):
        return self.generalList

    def setGeneralList(self, general):
        self.generalList = general

    def getAllPluginName(self):
        return list(self.plugins.keys())

    def getPlugin(self, pluginName):
        if pluginName in self.plugins:
            return self.plugins[pluginName]
        return None

    def getTarget(self, messageType: str, target: str):
        if (messageType in self.listener
                and target in self.listener[messageType]["targetListener"]):
            return self.listener[messageType]["targetListener"][target]
        return None

    def getHandleByTarget(self, messageType: str, target: str):
        if (re := self.getTarget(messageType, target)) is not None:
            return re.__self__
        return None

    def getTypeListener(self, messageType: str):
        if messageType in self.getListener():
            return self.getListener()[messageType]["typeListener"]
        return []

    def getTargetListener(self, messageType: str, target: str):
        if (messageType in self.getListener()
                and target in self.getListener()["targetListener"]):
            return self.getListener()["typeListener"][target]
        return []
