import asyncio
import concurrent.futures
import importlib
from multiprocessing import Process, SimpleQueue
from threading import Thread

from .BotException import BotException
from .GetModule import getRequest
from .JsonConfig import getConfig

threadSize = getConfig()["workThread"]
threadPool = concurrent.futures.ThreadPoolExecutor(
                max_workers=threadSize
            )


def asyncRunInThreadHandle(func, *args, **kwargs):
    try:
        loop = asyncio.get_event_loop()
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    asyncio.run(func(*args, **kwargs))


def runInThread(func, *args, **kwargs):
    global threadPool
    threadPool.submit(func, *args, **kwargs)


def asyncRunInThread(func, *args, **kwargs):
    runInThread(
        asyncRunInThreadHandle, func, *args, **kwargs
        )


def threadWorkFunction(queue):
    async def _threadWorkFunction():
        while True:
            data = queue.get()
            try:
                request = getRequest(data)
                module = importlib.reload(
                    importlib.import_module(request.getHandleModuleName()))
                plugin = getattr(module, "handle")()
                plugin.onLoad()
                if not plugin.initBySystem(request.getBot()):
                    return
                try:
                    await (plugin.getListener()[request.getType()]
                           ["targetListener"][request.getTarget()])(
                           request
                           )
                except Exception:
                    pass
            except Exception:
                pass
    try:
        loop = asyncio.get_event_loop()
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(_threadWorkFunction())


def processWorkFunction(queue):
    global threadSize
    processThreadPool = []
    processQueue = SimpleQueue
    for _ in range(threadSize):
        processThreadPool.append(
            Thread(target=threadWorkFunction,
                   args=(processQueue,)))
        processThreadPool[-1].start()
    while True:
        data = queue.get()
        processQueue.put(data)


class BotConcurrentModule:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def addTask(self, data):
        pass

    def runInThread(self, func, *args, **kwargs):
        pass

    def asyncRunInThread(self, func, *args, **kwargs):
        pass


class defaultBotConcurrentModule(BotConcurrentModule):
    def __init__(self, processSize, threadSize):
        if processSize == 0:
            raise BotException("错误的进程/线程数量")
        self.processList = []
        self.queue = SimpleQueue()
        for i in range(int(getConfig()["workProcess"])):
            self.processList.append(Process(
                target=processWorkFunction, args=(self.queue,)))
            self.processList[-1].start()
        global threadPool
        self.threadPool = threadPool

    def addTask(self, data):
        self.queue.put(data)

    def runInThread(self, func, *args, **kwargs):
        self.threadPool.submit(func, *args, **kwargs)

    def asyncRunInThread(self, func, *args, **kwargs):
        self.runInThread(
            asyncRunInThreadHandle(func, *args, **kwargs)
        )
