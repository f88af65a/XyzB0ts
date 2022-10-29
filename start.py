import botsdk.BotService
import botsdk.BotRoute
import botsdk.BotHandle
import botsdk.BotLoopEvent
import os
import sys
from botsdk.util.Args import GetArgs


def start():
    os.chdir(sys.path[0])
    args = GetArgs()
    if "service" in args:
        service = botsdk.BotService.BotService()
        service.run()
    if "route" in args:
        route = botsdk.BotRoute.BotRoute()
        route.run()
    if "handle" in args:
        handle = botsdk.BotHandle.BotHandle()
        handle.run()
    if "loopevent" in args:
        handle = botsdk.BotLoopEvent.BotLoopEvent()
        handle.run()


if __name__ == "__main__":
    start()
