import json
import os
import sys

from botsdk.util.BotException import BotException
from botsdk.util.JsonConfig import getConfig
from botsdk.util.Tool import getAttrFromModule


def getAdapter(data):
    return getAttrFromModule(
        getConfig()["botPath"].replace("/", ".")
        + data["botType"] + ".Adapter")(data)


class Adapter:
    def __init__(self, data):
        self.apiDict = {}
        self.loadAdapterFile(
            f"""{getConfig()["botPath"]}{data["botType"]}/adapter.json""")
        self.init(data)

    def init(self, data):
        pass

    def getApi(self):
        return self.apiDict

    def getData(self):
        return self.data

    def loadAdapterFile(self, filePath):
        if not (os.path.exists(filePath)
                and os.path.isfile(filePath)):
            raise BotException("adapter路径不存在")
        with open(filePath, "r") as f:
            self.data = json.loads(f.read())
            adapterData = self.data["api"]
        for i in adapterData:
            self.addMethod(i, adapterData[i]["path"],
                           adapterData[i]["method"],
                           adapterData[i]["parameter"])

    def addMethod(self, name, path, method, args):
        if name in self.apiDict:
            raise BotException("Adapter遇到了重复的api名称")
        self.apiDict[name] = {"path": path,
                              "parameter": args,
                              "method": method}

        async def forward(**kwargs):
            builtins = sys.modules['builtins']
            # 参数检查
            for i in args:
                if i not in kwargs:
                    raise BotException(f"adapter调用函数{name}缺少参数{i}")
                kwargs[i] = getattr(builtins, args[i])(kwargs[i])
            # 转发
            return await getattr(self, method)(
                self.apiDict[name], **kwargs)
        setattr(self, name, forward)
