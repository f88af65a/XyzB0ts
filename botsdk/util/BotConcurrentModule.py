import asyncio
import importlib
import threading
from multiprocessing import Process, Queue

from botsdk.BotRequest import BotRequest
from botsdk.util.BotException import BotException
from botsdk.util.Error import debugPrint, printTraceBack
from botsdk.util.HandlePacket import asyncHandlePacket
from botsdk.util.JsonConfig import getConfig


# 线程默认运行函数
def workThreadRun(loop):
    try:
        debugPrint("线程初始化")
        asyncio.set_event_loop(loop)
        debugPrint("线程进入循环")
        loop.run_forever()
    except Exception:
        printTraceBack("线程异常退出")


# 进程循环函数
async def workProcessRun(queue, threadList):
    debugPrint("进程进入循环")
    useThreadCount = 0
    while True:
        try:
            try:
                data = queue.get_nowait()
            except Exception:
                await asyncio.sleep(0.05)
                continue
            request = BotRequest(*data)
            module = importlib.reload(
                importlib.import_module(request.getHandleModuleName()))
            plugin = getattr(module, "handle")()
            if not plugin.initBySystem(request.getBot()):
                continue
            try:
                asyncio.run_coroutine_threadsafe(
                    asyncHandlePacket(
                        (plugin.getListener()[request.getType()]
                            ["targetListener"][request.getTarget()]),
                        request),
                    threadList[useThreadCount][1])
                useThreadCount += 1
                if useThreadCount == len(threadList):
                    useThreadCount = 0
            except Exception:
                printTraceBack()
        except Exception:
            printTraceBack()


# 进程初始化函数
def workProcessInit(queue, threadSize):
    debugPrint("新进程初始化")
    threadList = []
    debugPrint("线程创建中")
    for i in range(threadSize):
        loop = asyncio.new_event_loop()
        threadList.append(
            [threading.Thread(target=workThreadRun, args=(loop, )), loop])
    for i in threadList:
        i[0].start()
    debugPrint("线程创建完成")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    debugPrint("进程初始化完成")
    loop.run_until_complete(workProcessRun(queue, threadList))


class BotConcurrentModule:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def addTask(self, data):
        pass


class defaultBotConcurrentModule(BotConcurrentModule):
    def __init__(self, processSize, threadSize):
        if processSize * threadSize == 0:
            raise BotException("错误的进程/线程数量")
        self.processSize = processSize
        self.threadSize = threadSize
        self.processList = []
        self.queue = Queue()
        for i in range(int(getConfig()["workProcess"])):
            self.processList.append(Process(
                target=workProcessInit, args=(self.queue, threadSize)))
        for i in self.processList:
            i.start()

    def addTask(self, data):
        self.queue.put(data)