import os
import uuid
import json
import asyncio
from botsdk.tool.Error import printTraceBack
from botsdk.tool.JsonConfig import getConfig

class BotPlugin:
    def __init__(self):
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenType = []
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.listenTarget = []
        #[function1, ..., functionN]
        #return bool
        self.filterList = []
        #[function1, ..., f]
        self.formatList = []
        #"插件名称"
        self.name = ""
        #插件所定义的任务
        self.futures = dict()
        #是否可以分离到线程中安全执行
        self.canDetach = False
        #UUID
        self.uuid = uuid.uuid4()
        #配置文件,在pluginInit中初始化
        self.config = None
        #listener
        self.listener = {}
        #generalList
        self.generalList = []

    def __del__(self):
        pass

    def addType(self, typeName: str, func):
        if typeName not in self.getListener():
            self.getListener()[typeName] = {"typeListener": set(), "targetListener":{}}
        self.getListener()[typeName]["typeListener"].add(func)

    def addTarget(self, typeName: str, targetName: str, func):
        if typeName not in self.getListener():
            self.getListener()[typeName] = {"typeListener": set(), "targetListener":{}}
        self.getListener()[typeName]["targetListener"][targetName] = func
    
    def addGeneral(self, priority, func):
        self.getGeneralList().append((priority, func))
    
    def addFilter(self, func):
        self.addGeneral(5, func)
    
    def addFormat(self, func):
        self.addGeneral(6, func)

    #系统调用的初始化函数
    def initBySystem(self, bot):
        try:
            self.initPluginConfig()
            self.initTargetDict()
            self.init(bot)
        except Exception as e:
            self.clear()
            printTraceBack()
            return False
        return True

    def initTargetDict(self):
        self.targetDict = dict()
        for i in self.listenTarget:
            if i[0] not in self.targetDict:
                self.targetDict[i[0]] = dict()
            self.targetDict[i[0]][i[1]] = i[2]

    #配置文件初始化
    def initPluginConfig(self):
        pluginConfigPath = f'''./configs/{self.name}/config.json'''
        if os.path.exists(pluginConfigPath):
            with open(pluginConfigPath, "r") as configFile:
                self.config = json.loads(configFile.read())

    #在成功加载后才会调用
    def init(self, bot):
        pass

    #手动清理bot使用的资源
    def clear(self):
        pass

    def getListenType(self):
        return self.listenType

    def getListenTarget(self):
        return self.listenTarget

    def getFilterList(self):
        return self.filterList
    
    def getFormatList(self):
        return self.formatList

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
        self.getFutureDict()[name] = asyncio.run_coroutine_threadsafe(func, asyncio.get_event_loop())

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