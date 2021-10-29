import os
import sys
import importlib
from botsdk.tool.Error import *
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.JsonConfig import getConfig
from botsdk.tool.BotException import BotException

class BotPluginsManager:
    def __init__(self, bot):
        self.bot = bot
        #插件路径
        self.pluginsPath = getConfig()["pluginsPath"]
        #{插件名: 插件对象}
        self.plugins = dict()
        #{消息类型:{"typeListener":{func...}, "targetListener":{target:func...}}}
        self.listener = dict()
        #[(优先级,函数)]
        self.generalList = list()
    
    def __del__(self):
        for i in [i for i in self.plugins]:
            self.unLoadPlugin(i)

    def init(self):
        self.loadAllPlugin()

    def loadAllPlugin(self):
        for i in os.listdir(self.pluginsPath):
            self.loadPlugin(i)

    def reLoadPlugin(self, pluginName: str):
        if pluginName in self.plugins:
            path = f"{sys.modules[self.plugins[pluginName].__module__].__name__}.py"
            self.unLoadPlugin(pluginName)
            return self.loadPlugin(path)

    def loadPlugin(self, path: str):
        #检查是否存在以及是否是文件
        if not (os.path.exists(f"{self.pluginsPath}{path}") \
            and os.path.isfile(f"{self.pluginsPath}{path}")):
            return False
        path = path.replace(".py","")
        #加载
        try:
            module = importlib.reload(__import__(f"plugins.{path}", fromlist=(path,)))
            handle = getattr(module, "handle")()
        except Exception as e:
            printTraceBack()
            return False
        #检查名称是否重复
        if handle.getName() in self.plugins:
            return False
        #检查target是否重复
        handleListener = handle.getListener()
        for i in handleListener:
            for j in handleListener[i]:
                if i in self.getListener() and j in self.getListener()[i]["targetListener"]:
                    debugPrint(f"插件{handle.getName()} 类型{i}中使用了相同的target {j}")
                    return False
        #系统初始化
        if not handle.initBySystem(self.bot):
            return False
        #添加信息
        for i in handleListener:
            if i not in self.listener:
                self.listener[i] = {"typeListener":set(), "targetListener":dict()}
            self.listener[i]["typeListener"] |= handleListener[i]["typeListener"]
            self.listener[i]["targetListener"] |= handleListener[i]["targetListener"]
        self.generalList += handle.getGeneralList()
        self.generalList.sort(key = lambda i : i[0])
        self.plugins[handle.getName()] = handle
        return True

    def unLoadPlugin(self, pluginName: str):
        if (re := self.getPlugin(pluginName)) is not None:
            for i in re.getListener():
                for j in re.getListener()[i]["typeListener"]:
                    if i in self.listener and j in self.listener[i]["typeListener"]:
                        del self.listener[i]["typeListener"][j]
                for j in re.getListener()[i]["targetListener"]:
                    if i in self.listener and j in self.listener[i]["targetListener"]:
                        del self.listener[i]["targetListener"][j]
            for i in re.getGeneralList():
                self.generalList.remove(i)
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
        if messageType in self.listener and target in self.listener[messageType]["targetListener"]:
            return self.listener[messageType]["targetListener"][target]
        return None

    def getHandleByTarget(self, messageType: str, target: str):
        if (re := self.getTarget(messageType, target)) is not None:
            return re.__self__
        return None

    def getPluginPathByTarget(self, messageType: str, target: str):
        if (re := self.getHandleByTarget(messageType, target)) is not None:
            return sys.modules[re.__module__].__name__
        return None
    
    def getTypeListener(self, messageType: str):
        if messageType in self.getListener():
            return self.getListener()[messageType]["typeListener"]
        return []
    
    def getTargetListener(self, messageType: str, target: str):
        if messageType in self.getListener() and target in self.getListener()["targetListener"]:
            return self.getListener()["typeListener"][target]
        return []