import importlib
import os
import asyncio
import json
from botsdk.tool.MessageType import messageType
from botsdk.BotRequest import BotRequest
from botsdk.tool.Error import *
from botsdk.tool.JsonConfig import getConfig
from botsdk.tool.Permission import permissionCheck
from botsdk.tool.Permission import getPermissionFromSystem
from botsdk.tool.Permission import permissionCmp
from botsdk.tool.BotException import BotException
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.TimeTest import asyncTimeTest
from botsdk.tool.HandlePacket import asyncHandlePacket

class BotRoute:
    def __init__(self, bot, concurrentModule = None):
        self.bot = bot
        #插件目录路径
        self.pluginsPath = getConfig()["pluginsPath"]
        #{messageType:{target:func}}
        self.targetRoute = dict()
        #{messageType:{func}}
        self.typeRoute = dict()
        #{pluginName:pluginInstance}
        self.plugins = dict()
        #{pluginName:pluginFileName}
        self.pluginPath = dict()
        #{func}
        self.filterSet = set()
        self.concurrentModule = concurrentModule

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
        try:
            module = importlib.reload(__import__("plugins.{0}".format(path), fromlist=(path,)))
            handle = getattr(module, "handle")()
        except Exception as e:
            printTraceBack()
            return False
        if handle.getName() in self.pluginPath or handle.getName() in self.plugins:
            return False
        #检查是否有重复
        for i in handle.getListenTarget():
            if i[0] in self.targetRoute and i[1] in self.targetRoute[i[0]]:
                return False
        #初始化
        if not handle.initBySystem(self.bot):
            return False
        for i in handle.getListenType():
            self.addType(i[0], i[1])
        for i in handle.getListenTarget():
            self.addTarget(i[0], i[1], i[2])
        for i in handle.getFilterList():
            self.filterSet.add(i)
        self.pluginPath[handle.getName()] = path + ".py"
        self.plugins[handle.getName()] = handle
        return True

    def unLoadPlugin(self, pluginName: str):
        if pluginName in self.plugins:
            for i in self.plugins[pluginName].getListenType():
                self.removeType(i[0], i[1])
            for i in self.plugins[pluginName].getListenTarget():
                self.removeTarget(i[0], i[1], i[2])
            for i in [i for i in self.plugins[pluginName].getFutureDict()]:
                self.plugins[pluginName].removeFuture(i)
            for i in self.plugins[pluginName].getFilterList():
                self.filterSet.remove(i)
            del self.plugins[pluginName]
            del self.pluginPath[pluginName]

    def addTarget(self, messageType: str, target: str, func):
        if messageType not in self.targetRoute:
            self.targetRoute[messageType] = dict()
        if target in self.targetRoute[messageType]:
            raise BotException("插件使用了重复的Target")
        self.targetRoute[messageType][target] = func

    def removeTarget(self, messageType: str, target: str, func):
        if messageType in self.targetRoute and target in self.targetRoute[messageType]:
            del self.targetRoute[messageType][target]
     
    def addType(self, messageType: str, func):
        if messageType not in self.typeRoute:
            self.typeRoute[messageType] = set()
        self.typeRoute[messageType].add(func)

    def removeType(self, messageType: str, func):
        if messageType in self.typeRoute and func in self.typeRoute[messageType]:
            self.typeRoute[messageType].remove(func)

    def getAllPluginName(self):
        return list(self.plugins.keys())

    def getPlugin(self, pluginName):
        return self.plugins[pluginName]

    def getHandleByTarget(self, messageType: str, target : str):
        if messageType in self.targetRoute and target in self.targetRoute[messageType]:
            return self.targetRoute[messageType][target].__self__
        return None

    @asyncExceptTrace
    @asyncTimeTest
    async def route(self, request : BotRequest):
        #filter路由
        for i in self.filterSet:
            if not i(request):
                return
            await asyncio.sleep(0)
        #type路由
        if request.type in self.typeRoute:
            for i in self.typeRoute[request.type]:
                try:
                    await i(request)
                except Exception as e:
                    debugPrint(f"typeRoute中{str(i)}异常")
                await asyncio.sleep(0)
        if request.type not in messageType:
            return
        #命令分析
        target = request.getFirstTextSplit()
        #控制字段
        controlData = {"size":1}
        if target is not None and len(target) >= 2 and len(target[0]) > 2 \
            and target[0][0] == "[" and target[0][-1] == "]":
            if not permissionCmp(str(getPermissionFromSystem(request.getSenderId())), "ADMINISTRATOR"):
                await request.sendMessage(MessageChain().text("使用控制字段权限不足"))
                return
            controlList = target[0][1: -1].split("&")
            for i in controlList:
                controlLineSplit = i.split("=")
                if len(controlLineSplit) != 2:
                    debugPrint("控制字段格式出错")
                else:
                    if controlLineSplit[0] == "size":
                        controlData[controlLineSplit[0]] = json.loads(controlLineSplit[1])
            del target[0]
            request.getFirst("Plain")["text"] = " ".join(target)
        #target获取
        if target is None or len(target) == 0 or len(target[0]) == 0:
            return
        target = target[0]
        isTargetFlag = False
        for i in getConfig()["commandTarget"]:
            if len(target) >= len(i) and target[:len(i)] == i:
                target = target[len(i):]
                isTargetFlag = True
                break
        if not isTargetFlag:
            return
        #命令判断
        if request.type in self.targetRoute and target in self.targetRoute[request.type]:
            #权限判断
            if not permissionCheck(request, target):
                await request.sendMessage(MessageChain().text("权限限制"))
                return
            #路由
            for i in range(controlData["size"]):
                if self.concurrentModule is not None and self.getHandleByTarget(request.type, target).getCanDetach():
                    #多线程方式
                    bot = request.bot
                    self.concurrentModule.addTask( \
                        ((bot.path, bot.port, bot.sessionKey), \
                        [dict(request)], \
                        [self.pluginPath[self.getHandleByTarget(request.type, target).getName()][:-3], target]) \
                        )
                else:
                    await asyncHandlePacket(self.targetRoute[request.type][target], request)
