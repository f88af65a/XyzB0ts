import asyncio
import json
import re

from botsdk.BotRequest import BotRequest
from botsdk.util.BotConcurrentModule import defaultBotConcurrentModule
from botsdk.util.BotPluginsManager import BotPluginsManager
from botsdk.util.Error import debugPrint
from botsdk.util.HandlePacket import asyncHandlePacket
from botsdk.util.JsonConfig import getConfig
from botsdk.util.MessageChain import MessageChain
from botsdk.util.MessageType import messageType
from botsdk.util.Permission import getPermissionFromSystem, permissionCheck
from botsdk.util.Permission import permissionCmp


class BotRouter:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.init()

    def init(self):
        pass

    async def route(self, pluginsManager: BotPluginsManager,
                    request: BotRequest,
                    concurrentModule: defaultBotConcurrentModule = None):
        pass


class GeneralRouter(BotRouter):
    async def route(self, pluginsManager: BotPluginsManager,
                    request: BotRequest,
                    concurrentModule: defaultBotConcurrentModule = None):
        for i in pluginsManager.getGeneralList():
            if (ret := await i[1](request)) is not None and ret is False:
                return False
            await asyncio.sleep(0)
        return True


class TypeRouter(BotRouter):
    async def route(self, pluginsManager: BotPluginsManager,
                    request: BotRequest,
                    concurrentModule: defaultBotConcurrentModule = None):
        if request.getType() in pluginsManager.getListener():
            listener = pluginsManager.getListener()
            for i in listener[request.getType()]["typeListener"]:
                await i(request)
                await asyncio.sleep(0)
        return True


class TargetRouter(BotRouter):
    def init(self):
        self.pattern = re.compile(
            (r"^(\[(\S*?=\S*?)\])?(["
             + "".join(["\\" + i for i in getConfig()["commandTarget"]])
             + r"])(\S+)( \S+)*$"))

    async def route(self, pluginsManager: BotPluginsManager,
                    request: BotRequest,
                    concurrentModule: defaultBotConcurrentModule = None):
        if request.getType() not in messageType:
            return False
        # 命令提取
        target = request.getFirstTextSplit()
        if target is None:
            return
        # 正则匹配
        reData = self.pattern.search(target)
        # target获取
        if reData.group(4) is None:
            return
        target = reData.group(4)
        # 判断target是否存在
        isTargetFlag = False
        for i in getConfig()["commandTarget"]:
            if len(target) >= len(i) and target[:len(i)] == i:
                target = target[len(i):]
                isTargetFlag = True
                break
        if not isTargetFlag:
            return
        request.setTarget(target)
        # 控制字段判断
        controlData = {"size": 1}
        if reData.group(1) is not None:
            # 控制字段权限判断
            if not permissionCmp(
                    str(getPermissionFromSystem(request.getSenderId())),
                    "ADMINISTRATOR"):
                await request.sendMessage(MessageChain().plain("使用控制字段权限不足"))
                return
            # 控制字段提取
            controlList = reData.group(1).split("&")
            for i in controlList:
                controlLineSplit = i.split("=")
                if len(controlLineSplit) != 2:
                    debugPrint("控制字段格式出错")
                else:
                    if controlLineSplit[0] == "size":
                        controlData[controlLineSplit[0]] = (
                            json.loads(controlLineSplit[1]))
            request.setControlData(controlData)
        # 命令判断
        if (ret := pluginsManager.getTarget(
                request.getType(), target)) is not None:
            # 权限判断
            if not permissionCheck(request, target):
                await request.sendMessage(MessageChain().plain("权限限制"))
                return
            request.setHandleModuleName(
                pluginsManager.getHandleByTarget(
                    request.getType(), target).__module__)
            # 路由
            for i in range(controlData["size"]):
                if (concurrentModule is not None
                        and ret.__self__.getCanDetach()):
                    # 多进程方式
                    concurrentModule.addTask(request.getData())
                else:
                    await asyncHandlePacket(ret, request)
        return True
