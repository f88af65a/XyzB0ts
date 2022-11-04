from os import _exit
from threading import Lock
from .util.Error import printTraceBack


class Module:
    def __init__(self):
        self.exitList = []
        self.exitListLock = Lock()
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

    def init(self, *args, **kwargs):
        pass
