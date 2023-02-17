import os
import uuid

import ujson as json

from .Args import ArgParser
from .Error import printTraceBack
from .Cookie import AsyncGetCookie, AsyncSetCookie


class BotPlugin:
    def __init__(self):
        # 插件名称
        self.name = ""
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

    def addTargetWithArgs(self, typeName: str, targetName: str, func):
        argparser = ArgParser(help=func.__doc__)

        async def forward(request):
            args = request.getFirstTextSplit()[1:]
            if args is not None:
                try:
                    args = argparser.Parse(args)
                    if "help" in args:
                        if args["help"] is None:
                            await request.send(
                                argparser.GetHelp()
                                + "\n"
                                + targetName
                                + " "
                                + argparser.GetHelpLine()
                                + "\n"
                                + argparser.GetAllOptHelp()
                            )
                        else:
                            await request.send(
                                    argparser.GetOptHelp(args["help"]))
                        return
                except Exception as e:
                    await request.send(str(e))
                    return
                request.setArgs(dict(args))
            await func(request)
        if typeName not in self.getListener():
            self.getListener()[typeName] = {"typeListener": set(),
                                            "targetListener": dict()}
        forward.__doc__ = func.__doc__
        self.getListener()[typeName]["targetListener"][targetName] = forward
        return argparser

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

    def getUuid(self):
        return self.uuid

    def getConfig(self):
        return self.config

    def getListener(self):
        return self.listener

    def getGeneralList(self):
        return self.generalList

    # 持久化存储数据
    async def Push(self, key: str, value):
        '''
        持久化数据
        Push(key, value)
        key为要存储的数据的关键字
        value为需要存储的json数据
        若value为None则删除该数据
        '''
        return AsyncSetCookie(
            f"Plugin:{self.getName()}",
            key,
            value
        )

    async def Pull(self, key: str):
        '''
        获取持久化的数据
        Pull(key)
        key为要获取的数据的关键字
        '''
        return AsyncGetCookie(
            f"Plugin:{self.getName()}",
            key
        )
