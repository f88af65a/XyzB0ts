import botsdk.BotService
import multiprocessing
from botsdk.util.JsonConfig import getConfig

def start():
    if "startMethod" in getConfig():
        multiprocessing.set_start_method(getConfig()["startMethod"])
    service = botsdk.BotService.BotService()
    service.run()

if __name__ == "__main__":
    start()
