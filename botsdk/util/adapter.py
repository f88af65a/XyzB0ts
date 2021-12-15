import json
import os

from botsdk.util.BotException import BotException
from botsdk.util.Error import debugPrint


class Adapter:
    def __init__(self):
        self.apiDict = {}
        pass

    def getApi(self):
        return self.apiDict

    def loadAdapterFile(self, filePath):
        if not (os.path.exists(filePath)
                and os.path.isfile(filePath)):
            raise BotException("adapter路径不存在")
        adapterFile = json.loads(filePath)
        pass

    def addMethod(self, name, path, method, *args):
        if name in self.apiDict:
            raise BotException("Adapter遇到了重复的api名称")
        self.apiDict[name] = {"path": path, "parameter": args,
                              "method": method}
