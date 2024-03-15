import asyncio
import logging
from os import _exit
from threading import Lock

from .util.Error import debugPrint
from .util.JsonConfig import getConfig
from .util.MessageBus import GetMessageBus
from .util.Keeper import GetKeeper


class Module:
    def __init__(self, extend=None):
        self.exitList = []
        self.exitListLock = Lock()
        self.onStartList = list()
        self.onLoopList = list()
        self.mq = GetMessageBus()
        self.keeper = GetKeeper()
        self.init()
        self.extend = extend

    def addToExit(self, func, *args, **kwargs):
        self.exitListLock.acquire()
        self.exitList.append([func, args, kwargs])
        self.exitListLock.release()

    def exit(self):
        for i in self.exitList:
            try:
                i[0](*i[1], **i[2])
            except Exception as e:
                logging.exception(e)
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
            try:
                await i(self)
            except Exception as e:
                logging.exception(e)
                self.exit()

    def AddOnStart(self, f):
        self.onStartList.append(f)

    async def run(self):
        pass

    async def _start(self):
        try:
            await self.onStart()
            await self.run()
        except Exception as e:
            print(e)

    def start(self):
        loop = asyncio.get_event_loop()
        self.loop = loop
        asyncio.run_coroutine_threadsafe(
            self._start(),
            self.loop
        )

    async def sendMessage(self, topic, message: bytes):
        await self.mq.AsyncSendMessage(
            topic,
            message
        )

    async def deliveryReport(self, err, msg):
        if err is None:
            return
        debugPrint(f"消息发送失败:{err}", fromName="Module")
        self.sendMessge(
            msg.topic(),
            msg.value(),
            callback=self.deliveryReport
        )
