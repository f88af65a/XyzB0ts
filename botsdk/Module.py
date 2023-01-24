import asyncio
import logging
from os import _exit
from threading import Lock

from confluent_kafka import Producer

from .util.Error import debugPrint, printTraceBack
from .util.JsonConfig import getConfig


class Module:
    def __init__(self):
        self.exitList = []
        self.exitListLock = Lock()
        self.onStartList = list()
        self.onLoopList = list()
        self.p = Producer(
                {'bootstrap.servers': getConfig()["kafka"]}
            )
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
        await self.onStart()
        await self.run()

    def start(self):
        loop = asyncio.get_event_loop()
        self.loop = loop
        asyncio.run_coroutine_threadsafe(self._start(), self.loop)
        self.loop.run_forever()

    def sendMessage(self, topic, message: bytes):
        self.p.poll(0)
        self.p.produce(
            topic,
            message,
            callback=self.deliveryReport
        )
        self.p.flush()

    def deliveryReport(self, err, msg):
        if err is None:
            return
        debugPrint(f"消息发送失败:{err}", fromName="Module")
        self.sendMessge(
            msg.topic(),
            msg.value(),
            callback=self.deliveryReport
        )
