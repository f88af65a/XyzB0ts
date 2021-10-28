import os
import importlib
from botsdk.tool.Error import *
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.JsonConfig import getConfig
from botsdk.tool.BotException import BotException

class BotPluginsManager:
    def __init__(self):
        #插件路径
        self.pluginPath = getConfig()["pluginsPath"]
        #{插件名: 插件对象}
        self.plugins = dict()
        #{插件名:插件地址}
        self.pluginsPath = dict()
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
            path = self.pluginPath[pluginName]
            self.unLoadPlugin(pluginName)
            return self.loadPlugin(path)

    def loadPlugin(self, path: str):
        #检查是否存在以及是否是文件
        if not (os.path.exists(getConfig()["pluginsPath"] + path) \
            and os.path.isfile(getConfig()["pluginsPath"] + path)):
            return False
        path = path.replace(".py","")
        #加载
        try:
            module = importlib.reload(__import__("plugins.{0}".format(path), fromlist=(path,)))
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
        self.setListener(self.getListener() | handleListener)
        self.setGeneralList(self.getGeneralList() + handle.getGeneralList())
        self.getGeneralList().sort()
        self.pluginPath[handle.getName()] = path + ".py"
        self.plugins[handle.getName()] = handle
        return True

    def unLoadPlugin(self, pluginName: str):
        if (re := self.getPlugin(pluginName)) is not None:
            for i in re.getListener():
                for j in i["typeListener"]:
                    if i in self.getListener() and j in self.getListener()[i]["typeListener"]:
                        del self.getListener()[i]["typeListener"][j]
                for j in i["targetListener"]:
                    if i in self.getListener() and j in self.getListener()[i]["targetListener"]:
                        del self.getListener()[i]["targetListener"][j]
            for i in re.getGeneralList():
                self.getGeneralList().remove(i)
            del self.plugins[pluginName]
            del self.pluginPath[pluginName]

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
        if messageType in self.targetRoute and target in self.targetRoute[messageType]:
            return self.targetRoute[messageType][target]
        return None

    def getHandleByTarget(self, messageType: str, target: str):
        if (re := self.getTarget(messageType, target)) is not None:
            return re.__self__
        return None

    def getPluginPathByTarget(self, messageType: str, target: str):
        if (re := self.getHandleByTarget(messageType, target)) is not None:
            return self.pluginPath[re.getName()]
        return None
    
    def getTypeListener(self, messageType: str):
        if messageType in self.getListener():
            return self.getListener()[messageType]["typeListener"]
        return []
    
    
    def getTargetListener(self, messageType: str, target: str):
        if messageType in self.getListener() and target in self.getListener()["targetListener"]:
            return self.getListener()["typeListener"][target]
        return []