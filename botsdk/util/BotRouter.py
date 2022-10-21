import asyncio
import json
import re

from confluent_kafka import Producer

from .BotConcurrentModule import defaultBotConcurrentModule
from .BotPluginsManager import BotPluginsManager
from .Error import asyncTraceBack
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
                    request,
                    concurrentModule: defaultBotConcurrentModule = None):
        pass


class GeneralRouter(BotRouter):
    async def route(self,
                    pluginsManager: BotPluginsManager,
                    request,
                    concurrentModule: defaultBotConcurrentModule = None):
        for i in pluginsManager.getGeneralList():
            if request.getBot().getBotType() not in i[1].__self__.botSet:
                continue
            if (ret := await i[1](request)) is not None and ret is False:
                return False
        return True


class TypeRouter(BotRouter):
    async def route(self,
                    pluginsManager: BotPluginsManager,
                    request,
                    concurrentModule: defaultBotConcurrentModule = None):
        if request.getType() in pluginsManager.getListener():
            listener = pluginsManager.getListener()
            for i in listener[request.getType()]["typeListener"]:
                if request.getBot().getBotType() not in i.__self__.botSet:
                    continue
                await i(request)
        return True


class TargetRouter(BotRouter):
    def init(self):
        self.p = Producer({'bootstrap.servers': 'localhost:9092'})
        self.pattern = re.compile(
            (r"^(\[(\S*=\S*)&?\])?(["
             + "".join(["\\" + i for i in getConfig()["commandTarget"]])
             + r"])(\S+)( \S+)*$"))

    def deliveryReport(self, err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(
                    msg.topic(), msg.partition()))

    async def sendToHandle(self, func, request):
        self.p.poll(0)
        self.p.produce(
                "targetHandle",
                json.dumps(
                    {
                        "path": func.__module__,
                        "handle": func.__name__,
                        "request": request.getData()
                        }).encode("utf8"),
                callback=self.deliveryReport
        )
        self.p.flush()

    @asyncTraceBack
    async def route(self,
                    pluginsManager: BotPluginsManager,
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
            # 判断类型是否正确
            if request.getBot().getBotType() not in ret.__self__.botSet:
                return True
            # 权限判断
            if not await permissionCheck(request, target):
                await request.sendMessage("权限限制")
                return
            controlData = {"size": 1, "wait": 0}
            if reData.group(1) is not None:
                # 控制字段权限判断
                if not await roleCheck(
                        request,
                        {"System:Owner", "System:ADMINISTRATOR"}):
                    await request.sendMessage("使用控制字段权限不足")
                    return
                # 控制字段提取
                controlList = reData.group(1)[1:-1].split("&")
                for i in controlList:
                    controlLineSplit = i.split("=")
                    if len(controlLineSplit) != 2:
                        await request.sendMessage("控制字段有误")
                        return
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

        return True
