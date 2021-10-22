import time
from botsdk.tool.Error import printTraceBack
from botsdk.tool.Error import asyncExceptTrace
from botsdk.tool.Error import debugPrint
from botsdk.tool.TimeTest import *
from botsdk.BotRequest import BotRequest
from botsdk.tool.MessageChain import MessageChain

startCallBackTask = []
endCallBackTask = []

def asyncStartHandleNotify(func, *args, **kwargs):
    request = args[0]
    debugPrint(f"[asyncHandleTimeTest][{func.__name__}][{request.getFirstTextSplit()[0]}][{request.getUuid()}][START] time={time.time()}")

def asyncEndHandleNotify(func, *args, **kwargs):
    request = args[0]
    debugPrint(f"[asyncHandleTimeTest][{func.__name__}][{request.getFirstTextSplit()[0]}][{request.getUuid()}][END] time={time.time()}")

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

@asyncExceptTrace
@asyncTimeTest
async def asyncHandlePacket(fn, *args, **kwargs):
    try:
        for i in getStartCallBackTask():
            i(fn, *args, **kwargs)
        try:
            await fn(*args, **kwargs)
        except Exception as e:
            args[0].sendMessage(MessageChain().text(f"发生异常 str(e)"))
            raise e
        for i in getEndCallBackTask():
            i(fn, *args, **kwargs)
    except Exception as e:
        printTraceBack()

def HandlePacket(fn, *args, **kwargs):
    try:
        for i in getStartCallBackTask():
            i(fn, *args, **kwargs)
        try:
            fn(*args, **kwargs)
        except Exception as e:
            args[0].sendMessage(MessageChain().text(f"发生异常 str(e)"))
            raise e
        for i in getEndCallBackTask():
            i(fn, *args, **kwargs)
    except Exception as e:
        printTraceBack()