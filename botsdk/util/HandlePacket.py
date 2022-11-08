import asyncio
import time

from .Error import asyncTraceBack, debugPrint, printTraceBack
from .TimeTest import asyncTimeTest

startCallBackTask = []
endCallBackTask = []


def asyncStartHandleNotify(func, *args, **kwargs):
    # request = args[0]
    debugPrint((f'''[{func.__name__}]'''
                "[START]"
                f'''{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}'''
                ))


def asyncEndHandleNotify(func, *args, **kwargs):
    # request = args[0]
    debugPrint((f'''[{func.__name__}]'''
                "[END]"
                f'''{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}'''
                ))


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
            if "controlData" in request.getData()[0]:
                controlData = request.getControlData()
                for i in range(int(controlData["size"])):
                    await asyncio.sleep(int(controlData["wait"]))
                    await func(*args, **kwargs)
            else:
                await func(*args, **kwargs)
        except Exception as e:
            await args[0].sendMessage(f"执行过程中发生异常 {str(e)}")
            raise e
        for i in getEndCallBackTask():
            i(func, *args, **kwargs)
    except Exception:
        printTraceBack()
