import time
from botsdk.util.Error import debugPrint


def timeTest(func):
    def warp(*args, **kwargs):
        startTime = time.time()
        re = func(*args, **kwargs)
        debugPrint(
            f"[{func.__name__}]{str(time.time() - startTime)}")
        return re
    return warp


def asyncTimeTest(func):
    async def warp(*args, **kwargs):
        startTime = time.time()
        re = await func(*args, **kwargs)
        debugPrint(
            f"[{func.__name__}]{str(time.time() - startTime)}")
        return re
    return warp
