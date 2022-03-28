import asyncio
import re

from botsdk.util.BotConcurrentModule import defaultBotConcurrentModule
from botsdk.util.BotPluginsManager import BotPluginsManager
from botsdk.util.Error import asyncTraceBack
from botsdk.util.HandlePacket import asyncHandlePacket
from botsdk.util.JsonConfig import getConfig
from botsdk.util.Permission import permissionCheck


class BotRouter:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.init()

    def init(self):
        pass

    async def route(self, pluginsManager: BotPluginsManager,
                    request,
                    concurrentModule: defaultBotConcurrentModule = None):
        pass


class GeneralRouter(BotRouter):
    async def route(self, pluginsManager: BotPluginsManager,
                    request,
                    concurrentModule: defaultBotConcurrentModule = None):
        for i in pluginsManager.getGeneralList():
            if (ret := await i[1](request)) is not None and ret is False:
                return False
            await asyncio.sleep(0)
        return True


class TypeRouter(BotRouter):
    async def route(self, pluginsManager: BotPluginsManager,
                    request,
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
            (r"^(\[(\S*=\S*)&?\])?(["
             + "".join(["\\" + i for i in getConfig()["commandTarget"]])
             + r"])(\S+)( \S+)*$"))

    @asyncTraceBack
    async def route(self, pluginsManager: BotPluginsManager,
                    request,
                    concurrentModule: defaultBotConcurrentModule = None):
        # 类型判断与命令获取
        if (target := request.getFirstText()) is None or not target:
            return False
        # 正则匹配
        reData = self.pattern.search(target)
        # target获取
        if reData is None or reData.group(4) is None:
            return
        target = reData.group(4)
        request.setTarget(target)
        # 命令判断
        if (ret := pluginsManager.getTarget(
                request.getType(), target)) is not None:
            # 权限判断
            if not await permissionCheck(request, target):
                await request.sendMessage("权限限制")
                return
            controlData = {"size": 1, "wait": 0}
            '''
            if reData.group(1) is not None:
                # 控制字段权限判断
                if not permissionCmp(
                        str(getPermissionFromSystem(request.getUserId())),
                        "ADMINISTRATOR"):
                    await request.sendMessage(
                        MessageChain().plain("使用控制字段权限不足"))
                    return
                # 控制字段提取
                controlList = reData.group(1)[1:-1].split("&")
                for i in controlList:
                    controlLineSplit = i.split("=")
                    if len(controlLineSplit) != 2:
                        MessageChain().plain("控制字段有误")
                        return
                    else:
                        controlData[controlLineSplit[0]] = controlLineSplit[1]
            '''
            request.setControlData(controlData)
            # 设置处理模块名
            request.setHandleModuleName(
                pluginsManager.getHandleByTarget(
                    request.getType(), target).__module__)
            # 路由
            if (concurrentModule is not None
                    and ret.__self__.getCanDetach()
                    and request.getBot().getCanDetach()):
                # 多进程方式
                concurrentModule.addTask(request.getData())
            else:
                await asyncHandlePacket(ret, request)
        return True
