import json
import asyncio
from botsdk.tool.Error import *
from botsdk.tool.Permission import *
from botsdk.BotRequest import BotRequest
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.MessageType import messageType
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.HandlePacket import asyncHandlePacket
from botsdk.tool.BotPluginsManager import BotPluginsManager
from botsdk.tool.BotConcurrentModule import defaultBotConcurrentModule

class BotRouter:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def route(self, pluginsManager: BotPluginsManager, request: BotRequest \
        , concurrentModule: defaultBotConcurrentModule=None):
        pass

class GeneralRouter(BotRouter):
    async def route(self, pluginsManager: BotPluginsManager, request: BotRequest \
        , concurrentModule: defaultBotConcurrentModule=None):
        for i in pluginsManager.getGeneralList():
            if (re := await i[1](request)) is not None and re is False:
                return False
            await asyncio.sleep(0)
        return True

class TypeRouter(BotRouter):
    async def route(self, pluginsManager: BotPluginsManager, request: BotRequest \
        , concurrentModule: defaultBotConcurrentModule=None):
        if request.getType() in pluginsManager.getListener():
            for i in pluginsManager.getListener()[request.getType()]["typeListener"]:
                await i(request)
                await asyncio.sleep(0)
        return True

class TargetRouter(BotRouter):
    async def route(self, pluginsManager: BotPluginsManager, request: BotRequest \
        , concurrentModule: defaultBotConcurrentModule=None):
        if  request.getType() not in messageType:
            return False
        #命令分析
        target = request.getFirstTextSplit()
        #控制字段
        controlData = {"size": 1}
        if target is not None and len(target) >= 2 and len(target[0]) > 2 \
            and target[0][0] == "[" and target[0][-1] == "]":
            if not permissionCmp(str(getPermissionFromSystem(request.getSenderId())), "ADMINISTRATOR"):
                await request.sendMessage(MessageChain().plain("使用控制字段权限不足"))
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
            request.setControlData(controlData)
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
        request.setTarget(target)
        #命令判断
        if (re := pluginsManager.getTarget(request.getType(), target)) is not None:
            #权限判断
            if not permissionCheck(request, target):
                await request.sendMessage(MessageChain().plain("权限限制"))
                return
            request.setHandleModuleName(pluginsManager.getHandleByTarget(request.getType(), target).__module__)
            #路由
            for i in range(controlData["size"]):
                if concurrentModule is not None and re.__self__.getCanDetach():
                    #多进程方式
                    concurrentModule.addTask(request.getData())
                else:
                    await asyncHandlePacket(re, request)
        return True