import json
import os
from botsdk.tool.BotException import BotException

config = None
configDirPath = "./configs/"

def load():
    global config
    try:
        with open(configDirPath + "config.json") as configFile:
            config = json.loads(configFile.read())
    except Exception as e:
        print("Config.json读取出错")
        raise BotException("配置文件读取出错")
        return False
    return True
load()

def reload():
    return load()

def getConfig():
    global config
    return config

def checkLocalFile():
    if not os.path.exists(getConfig()["localFilePath"]):
        raise BotException("localFile不存在")
checkLocalFile()