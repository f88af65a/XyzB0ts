import time
import asyncio

from botsdk.util.Error import asyncTraceBack, debugPrint, printTraceBack
from botsdk.util.MessageChain import MessageChain
from botsdk.util.TimeTest import asyncTimeTest

startCallBackTask = []
endCallBackTask = []


def asyncStartHandleNotify(func, *args, **kwargs):
    request = args[0]
    debugPrint((f"[asyncHandleTimeTest][{func.__name__}]"
                f"[{request.getFirstTextSplit()[0]}][{request.getUuid()}]"
                f"[{request.getId()}][START] time={time.time()}"))


def asyncEndHandleNotify(func, *args, **kwargs):
    request = args[0]
    debugPrint((f"[asyncHandleTimeTest][{func.__name__}]"
                f"[{request.getFirstTextSplit()[0]}][{request.getUuid()}]"
                f"[{request.getId()}][END] time={time.time()}"))


def addToStartCallBack(func):
    global startCallBackTask
    startCallBackTask.append(func)


def addToEndCallBack(func):
    global endCallBackTask
    endCallBackTask.append(func)


addToStartCallBack(asyncStartHandleNotify)
addToEndCallBack(asyncEndHandleNotify)


def getStartCallBackTask():
    global startCallBackTask
    return startCallBackTask


def getEndCallBackTask():
    global endCallBackTask
    return endCallBackTask


@asyncTraceBack
@asyncTimeTest
async def asyncHandlePacket(func, *args, **kwargs):
    try:
        for i in getStartCallBackTask():
            i(func, *args, **kwargs)
        try:
            request = args[0]
            controlData = request.getControlData()
            for i in range(int(controlData["size"])):
                await asyncio.sleep(int(controlData["wait"]))
                await func(*args, **kwargs)
        except Exception as e:
            await args[0].sendMessage(
                MessageChain().text(f"执行过程中发生异常 {str(e)}"))
            raise e
        for i in getEndCallBackTask():
            i(func, *args, **kwargs)
    except Exception:
        printTraceBack()
