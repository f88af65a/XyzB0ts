import botsdk.BotService
import botsdk.BotRoute
import botsdk.BotHandle
import botsdk.BotLoopEvent
import os
import sys
from botsdk.util.Args import GetArgs
from botsdk.util.Cookie import InitAsyncCookieDriver


def start():
    os.chdir(sys.path[0])
    args = GetArgs()
    handle = None
    if "service" in args:
        handle = botsdk.BotService.BotService()
    if "route" in args:
        handle = botsdk.BotRoute.BotRoute()
    if "handle" in args:
        handle = botsdk.BotHandle.BotHandle()
    if "loopevent" in args:
        handle = botsdk.BotLoopEvent.BotLoopEvent()
    handle.AddOnStart(InitAsyncCookieDriver)
    handle.start()


if __name__ == "__main__":
    start()
