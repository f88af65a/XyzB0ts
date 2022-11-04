import asyncio
import ujson as json
import re

from confluent_kafka import Producer

from .TimeTest import asyncTimeTest

from .BotPluginsManager import BotPluginsManager
from .Error import asyncTraceBack, debugPrint
from .JsonConfig import getConfig
from .Permission import permissionCheck, roleCheck


class BotRouter:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.init()

    def init(self):
        pass

    async def route(self,
                    pluginsManager: BotPluginsManager,
                    request):
        pass


class GeneralRouter(BotRouter):
    @asyncTimeTest
    async def route(self,
                    pluginsManager: BotPluginsManager,
                    request):
        for i in pluginsManager.getGeneralList():
            if request.getBot().getBotType() not in i[1].__self__.botSet:
                continue
            if (ret := await i[1](request)) is not None and ret is False:
                return [False, i]
        return [True, None]


class TypeRouter(BotRouter):
    @asyncTimeTest
    async def route(self,
                    pluginsManager: BotPluginsManager,
                    request):
        if request.getType() in pluginsManager.getListener():
            listener = pluginsManager.getListener()
            for i in listener[request.getType()]["typeListener"]:
                if request.getBot().getBotType() not in i.__self__.botSet:
                    continue
                await i(request)
        return [True, None]


class TargetRouter(BotRouter):
    def init(self):
        self.pattern = re.compile(
            (r"^(\[(\S*=\S*)&?\])?(["
             + "".join(["\\" + i for i in getConfig()["commandTarget"]])
             + r"])(\S+)( \S+)*$"))
        self.p = Producer({'bootstrap.servers': 'localhost:9092'})

    def deliveryReport(self, err, msg):
        if err is not None:
            debugPrint('Message delivery failed: {}'.format(err))
        else:
            debugPrint('Message delivered to {} [{}]'.format(
                    msg.topic(), msg.partition()))

    async def sendToHandle(self, func, request):
        self.p.poll(0)
        self.p.produce(
                "targetHandle",
                json.dumps(
                    {"code": 0,
                     "data": {
                        "path": func.__module__,
                        "handle": func.__name__,
                        "request": request.getData()
                        }}).encode("utf8"),
                callback=self.deliveryReport
        )
        self.p.flush()

    @asyncTraceBack
    @asyncTimeTest
    async def route(self,
                    pluginsManager: BotPluginsManager,
                    request):
        # 类型判断与命令获取
        if (target := request.getFirstText()) is None or not target:
            return [False, None]
        # 正则匹配
        reData = self.pattern.search(target)
        # target获取
        if reData is None or reData.group(4) is None:
            return [False, None]
        target = reData.group(4)
        request.setTarget(target)
        # 命令判断
        if (ret := pluginsManager.getTarget(
                request.getType(), target)) is not None:
            # 判断类型是否正确
            if request.getBot().getBotType() not in ret.__self__.botSet:
                return [True, None]
            # 权限判断
            if not await permissionCheck(request, target):
                await request.sendMessage("权限限制")
                return [False, None]
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
            # 设置处理模块名
            request.setHandleModuleName(
                pluginsManager.getHandleByTarget(
                    request.getType(), target).__module__)
            '''
            1.0 update
            # 路由
            if (concurrentModule is not None
                    and ret.__self__.getCanDetach()
                    and request.getBot().getCanDetach()):
                # 多进程方式
                concurrentModule.addTask(request.getData())
            else:
                await asyncHandlePacket(ret, request)
            '''
            await self.sendToHandle(ret, request)
        return [True, None]
