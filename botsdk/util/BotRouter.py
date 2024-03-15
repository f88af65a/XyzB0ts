import asyncio
import re

import ujson as json
from thefuzz import fuzz

from .BotPluginsManager import BotPluginsManager
from .Error import asyncTraceBack, debugPrint, printTraceBack
from .JsonConfig import getConfig
from .Permission import permissionCheck, roleCheck
from .TimeTest import asyncTimeTest


class BotRouter:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.init()

    def init(self):
        pass

    async def route(self,
                    pluginsManager: BotPluginsManager,
                    route,
                    request):
        pass


class GeneralRouter(BotRouter):
    @asyncTimeTest
    async def route(self,
                    pluginsManager: BotPluginsManager,
                    route,
                    request):
        for i in pluginsManager.getGeneralList():
            if request.getBot().getBotType() not in i[1].__self__.botSet:
                continue
            try:
                if (ret := await i[1](request)) is not None and ret is False:
                    return [False, i]
            except Exception:
                debugPrint(
                    f"在执行{i}时发生异常",
                    fromName="GeneralRouter"
                )
                printTraceBack()
                return [False, i]
        return [True, None]


class TypeRouter(BotRouter):
    async def sendToHandle(self, route, request):
        await route.sendMessage(
                "targetHandle",
                json.dumps(
                    {
                        "code": 0,
                        "data": {
                            "msgType": 0,
                            "type": request.getType(),
                            "request": request.getData()
                        }
                    }
                ).encode("utf8")
        )
        debugPrint(
            f"{request.getUuid()}转发至handle",
            fromName="TypeRouter"
        )

    @asyncTimeTest
    async def route(self,
                    pluginsManager: BotPluginsManager,
                    route,
                    request):
        await self.sendToHandle(route, request)
        debugPrint(
            f"{request.getUuid()}转发至handle",
            fromName="TypeRouter"
        )
        return [True, None]


class TargetRouter(BotRouter):
    def init(self):
        self.cmdTarget = tuple(getConfig()["commandTarget"])
        self.pattern = re.compile(
            (r"^(\[(\S*=\S*)&?\])?(["
             + "".join(["\\" + i for i in getConfig()["commandTarget"]])
             + r"])(\S+)( \S+)*$"))

    async def sendToHandle(self, route, target, request):
        await route.sendMessage(
            "targetHandle",
            json.dumps(
                {
                    "code": 0,
                    "data": {
                        "msgType": 1,
                        "target": target,
                        "request": request.getData()
                    }
                }
            ).encode("utf8")
        )
        debugPrint(
            f"{request.getUuid()}转发至handle",
            fromName="TargetRouter"
        )

    @asyncTraceBack
    @asyncTimeTest
    async def route(self,
                    pluginsManager: BotPluginsManager,
                    route,
                    request):
        # 类型判断与命令获取
        if (target := request.getFirstText()) is None or not target:
            return [False, None]
        if not target.startswith(self.cmdTarget):
            return [False, None]
        for i in self.cmdTarget:
            if target.startswith(i):
                target = target[len(i):]
                break
        if ":" in target:
            needRole = ":".join(target.split(":")[:-1])
            if not await roleCheck(request, {needRole}):
                await request.sendMessage("权限限制")
                return [True, None]
        request.setTarget(target)
        # 命令判断
        if (ret := pluginsManager.getTarget(
                request.getType(), target)) is not None:
            # 判断类型是否正确
            if (request.getBot().getBotType()
                    not in pluginsManager.getPluginByHandle(ret).botSet):
                return [True, None]
            # 权限判断
            if not await permissionCheck(request, target):
                await request.sendMessage("权限限制")
                return [False, None]
            '''
            controlData = {"size": 1, "wait": 0}
            if reData.group(1) is not None:
                # 控制字段权限判断
                if not await roleCheck(
                        request,
                        {"System:Owner", "System:ADMINISTRATOR"}):
                    await request.sendMessage("使用控制字段权限不足")
                    return [False, None]
                # 控制字段提取
                controlList = reData.group(1)[1:-1].split("&")
                for i in controlList:
                    controlLineSplit = i.split("=")
                    if len(controlLineSplit) != 2:
                        await request.sendMessage("控制字段有误")
                        return [False, None]
                    else:
                        controlData[controlLineSplit[0]] = controlLineSplit[1]
            request.setControlData(controlData)
            '''
            # 设置处理模块名
            request.setHandleModuleName(
                pluginsManager.getHandleByTarget(
                    request.getType(), target).__module__)
            await self.sendToHandle(route, target, request)
        else:
            targets = pluginsManager.getTargetByType(request.getType())
            if targets:
                helpTargets = []
                for i in range(len(targets)):
                    if fuzz.ratio(targets[i], target) >= 60:
                        helpTargets.append(targets[i])
                if helpTargets:
                    await request.send("TIPS:\n" + "\n".join(helpTargets))
        return [True, None]
