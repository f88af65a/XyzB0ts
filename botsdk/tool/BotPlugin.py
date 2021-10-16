import uuid
import asyncio
from botsdk.Bot import Bot
from botsdk.tool.JsonConfig import getConfig

#在load中实例化，确认name和target不重复后会调用init()
#在unload中析构
class BotPlugin:
    def __init__(self):
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

    def __del__(self):
        pass

    def addType(typeName: str):
        def forward(func):
            func.__self__.addTypeToList(typeName, func)
            return func
        return forward

    def addTarget(typeName: str, targetName: str):
        def forward(func):
            func.__self__.addTargetToList(typeName, targetName, func)
            return func
        return forward

    def addFilter(func):
        func.__self__.addFilterToList(func)
        return func

    def addTypeToList(self, typeName: str, func):
        self.listenType.append([typeName, func])

    def addTargetToList(self, typeName: str, targetName: str, func):
        self.listenType.append([typeName, targetName, func])
    
    def addFilterToList(self, func):
        self.listenType.append(func)
    
    #在成功加载后才会调用
    def init(self, bot):
        pass

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
        return getConfig(self.__class__.__name__)
