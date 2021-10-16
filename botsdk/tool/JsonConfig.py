import json
import sys
import os

config = None
pluginsConfig = dict()
configDirPath = "./configs/"

def load():
    global config
    try:
        with open(configDirPath + "config.json") as configFile:
            config = json.loads(configFile.read())
    except Exception as e:
        print("Config.json读取出错")
        return False
    pluginsConfigDir = os.listdir(configDirPath)
    for i in pluginsConfigDir:
        if os.path.isdir(configDirPath + i) and os.path.exists(configDirPath + i + "/config.json"):
            try:
                with open(configDirPath + i + "/config.json") as pluginConfigFile:
                    config = json.loads(pluginConfigFile.read())
                    pluginsConfig[i] = config
            except Exception as e:
                print(f"{i} 配置文件读取出错")
                return False
    config["runPath"] = os.argv[0]
    return True
load()

def reload():
    return load()

def getConfig(pluginName: str = None):
    global config
    global pluginsConfig
    if pluginName is not None:
        if pluginName in pluginsConfig:
            return pluginsConfig[pluginName]
        return None
    return config
