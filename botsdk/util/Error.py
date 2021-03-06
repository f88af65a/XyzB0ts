import traceback

from .JsonConfig import getConfig
from .RunInThread import runInThread


def debugPrint(msg: str, fromName=None, exception=None, level=5):
    if level <= getConfig()["debugPrint"]:
        runInThread(
            print,
            ((f"[{str(fromName)}]" if fromName is not None else "")
             + (f"[{str(exception)}]" if exception is not None else "")
             + str(msg))
            )


def exceptionExit(msg):
    debugPrint(msg)
    exit()


def printTraceBack(msg=None):
    traceback.print_exc()
    if msg is not None:
        debugPrint(msg)


def traceBack(func):
    def warp(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            printTraceBack()
            return None
    return warp


def asyncTraceBack(func):
    async def warp(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            printTraceBack()
            return None
    return warp
