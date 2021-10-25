import os
import uuid
import json
import asyncio
from botsdk.tool.Error import printTraceBack
from botsdk.tool.JsonConfig import getConfig

class BotPlugin:
    def __init__(self):
        '''
        在load中实例化，确认name和target不重复后会调用init()
        在unload中析构
        listenType用于监听某一类型消息
        listenTarget用于监听关键字，具体处理方法见BotRoute.route
        filterList用于自定义过滤，返回bool，若为False则不再处理该消息
        在继承BotPlugin后可以通过addType/addTarget/addFilter函数进行注册或者直接重载相关list
        addFuture用于在init时向eventLoop中添加future
        listenType/listenTarget/filterList/futures在unload时会由BotRoute清理
        clean用于在init出错时手动清理相关资源
        canDetach用于标记可跨进程插件，会在route时交由其它进程处理
        '''
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenType = []
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.listenTarget = []
        #[function1, ..., functionN]
        #return bool
        self.filterList = []
        #"插件名称"
        self.name = ""
        #"插件信息"
        self.info = ""
        #"插件帮助"
        self.help = ""
        #插件所定义的任务
        self.futures = dict()
        #是否可以分离到线程中安全执行
        self.canDetach = False
        #UUID
        self.uuid = uuid.uuid4()
        #配置文件,在pluginInit中初始化
        self.config = None

    def __del__(self):
        pass

    def addType(self, typeName: str, func):
        self.listenType.append([typeName, func])

    def addTarget(self, typeName: str, targetName: str, func):
        self.listenTarget.append([typeName, targetName, func])
    
    def addFilter(self, func):
        self.filterList.append(func)
    
    #初始化相关函数

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

    #初始化失败调用
    def clear(self):
        pass

    def getListenType(self):
        return self.listenType

    def getListenTarget(self):
        return self.listenTarget

    def getFilterList(self):
        return self.filterList

    def getName(self):
        return self.name

    def getInfo(self):
        return self.info

    def getHelp(self):
        return self.help

    def getFutureDict(self):
        return self.futures

    def getFutureByName(self, name):
        if name in self.futures:
            return self.futures[name]
        return None

    def addFuture(self, name, func):
        if name in self.futures:
            return None
        self.futures[name] = asyncio.run_coroutine_threadsafe(func, asyncio.get_event_loop())

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

    def getTargetDict(self):
        return self.targetDict