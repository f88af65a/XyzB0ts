import asyncio
import concurrent.futures

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
