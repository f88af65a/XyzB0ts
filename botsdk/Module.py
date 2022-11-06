from os import _exit
from threading import Lock
from .util.Error import printTraceBack
import asyncio


class Module:
    def __init__(self):
        self.exitList = []
        self.exitListLock = Lock()
        self.onStartList = list()
        self.onLoopList = list()
        self.init()

    def addToExit(self, func, *args, **kwargs):
        self.exitListLock.acquire()
        self.exitList.append([func, args, kwargs])
        self.exitListLock.release()

    def exit(self):
        for i in self.exitList:
            try:
                i[0](*i[1], **i[2])
            except Exception:
                printTraceBack()
        _exit(1)

    '''
    初始化流程:
    __init__ -> init -> start -> (进入loop)
    -> onStart -> run
    '''

    def init(self, *args, **kwargs):
        pass

    async def onStart(self):
        for i in self.onStartList:
            await i(self)

    def AddOnStart(self, f):
        self.onStartList.append(f)

    async def run(self):
        pass

    async def _start(self):
        await self.onStart()
        await self.run()

    def start(self):
        loop = asyncio.get_event_loop()
        self.loop = loop
        asyncio.run_coroutine_threadsafe(self._start(), self.loop)
        self.loop.run_forever()
