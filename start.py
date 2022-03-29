import botsdk.BotService
import multiprocessing
import os
import sys
from botsdk.util.JsonConfig import getConfig


def start():
    if "startMethod" in getConfig():
        multiprocessing.set_start_method(getConfig()["startMethod"])
    os.chdir(sys.path[0])
    service = botsdk.BotService.BotService()
    service.run()


if __name__ == "__main__":
    start()
