from os import _exit

from .util.Error import printTraceBack


class Module:
    def __init__(self):
        self.exitList = []
        self.init()

    def addToExit(self, func, *args, **kwargs):
        self.exitList.append([func, args, kwargs])

    def exit(self):
        for i in self.exitList:
            try:
                i[0](*i[1], **i[2])
            except Exception:
                printTraceBack()
        _exit(1)

    def init(self, *args, **kwargs):
        pass
