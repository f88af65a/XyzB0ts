import botsdk.BotService
import botsdk.BotRoute
import botsdk.BotHandle
import botsdk.BotLoopEvent
import os
import sys
from botsdk.util.Args import GetArgs
from botsdk.util.JsonConfig import getConfig
from botsdk.util.Cookie import InitAsyncCookieDriver
import asyncio


async def main():
    await InitAsyncCookieDriver()
    modules = [
        botsdk.BotRoute.BotRoute(),
        botsdk.BotHandle.BotHandle(),
        botsdk.BotLoopEvent.BotLoopEvent()
    ]
    for i in getConfig()["account"]:
        modules.append(
            botsdk.BotService.BotService({"account": i})
        )
    for i in modules:
        i.start()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    os.chdir(sys.path[0])
    asyncio.run(
        main()
    )
