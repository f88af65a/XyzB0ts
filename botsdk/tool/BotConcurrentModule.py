import asyncio
import threading
import importlib
from multiprocessing import Process, Queue
from botsdk.Bot import Bot
from botsdk.BotRequest import BotRequest
from botsdk.tool.BotException import BotException
from botsdk.tool.JsonConfig import getConfig
from botsdk.tool.TimeTest import *
from botsdk.tool.Error import printTraceBack,debugPrint
from botsdk.tool.HandlePacket import *

#线程默认运行函数
def workThreadRun(loop):
    try:
        debugPrint("线程初始化")
        asyncio.set_event_loop(loop)
        debugPrint("线程进入循环")
        loop.run_forever()
    except Exception as e:
        printTraceBack("线程异常退出")


#进程循环函数
async def workProcessRun(queue, threadList):
    loop = asyncio.get_event_loop()
    debugPrint("进程进入循环")
    useThreadCount = 0
    while True:
        try:
            try:
                event = queue.get_nowait()
            except Exception as e:
                await asyncio.sleep(0.05)
                continue
            bot = Bot(*event[0])
            request = BotRequest(event[1][0], bot)
            module = importlib.reload(__import__(f"plugins.{event[2][0]}", fromlist=(event[2][0],)))
            plugin = getattr(module, "handle")()
            plugin.init()
            plugin.pluginInit()
            handle = None
            for i in plugin.getListenTarget():
                if i[1] == event[2][1]:
                    handle = i[2]
                    break
            if handle is not None:
                debugPrint("添加到协程中")
                asyncio.run_coroutine_threadsafe(asyncHandlePacket(handle, request), threadList[useThreadCount][1])
                debugPrint("添加完成")
                useThreadCount += 1
                if useThreadCount == len(threadList):
                    useThreadCount = 0
            else:
                debugPrint("进程遇到错误的Target")
        except Exception as e:
            printTraceBack()

#进程初始化函数
def workProcessInit(queue, threadSize):
    debugPrint("新进程初始化")
    threadList = []
    debugPrint("线程创建中")
    for i in range(threadSize):
        loop = asyncio.new_event_loop()
        threadList.append([threading.Thread(target = workThreadRun, args = (loop, )), loop])
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
            self.processList.append(Process(target=workProcessInit, args=(self.queue, threadSize)))
        for i in self.processList:
            i.start()

    def addTask(self,data):
        self.queue.put(data)
