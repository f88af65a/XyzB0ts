import json
import os
import sys

import botsdk.util.HttpRequest
from botsdk.util.BotException import BotException
from botsdk.util.JsonConfig import getConfig


def getAdapter(adapterName: str, url: str):
    return getattr(sys.modules[__name__], adapterName)(url)


class Adapter:
    def __init__(self, url):
        self.url = url
        self.apiDict = {}
        self.init()
        self.loadAdapterFile(getConfig()["adapterPath"] + self.adapterFileName)

    def init(self):
        pass

    def getApi(self):
        return self.apiDict

    def loadAdapterFile(self, filePath):
        if not (os.path.exists(filePath)
                and os.path.isfile(filePath)):
            raise BotException("adapter路径不存在")
        with open(filePath, "r") as f:
            adapterData = json.loads(f.read())["api"]
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


class MiraiAdapter(Adapter):
    def init(self):
        self.adapterFileName = "mirai.json"

    async def get(self, parameter, **kwargs):
        return json.loads(
            await botsdk.util.HttpRequest.get(
                (self.url + parameter["path"] + "?"
                 + "&".join(["=".join([i, kwargs[i]]) for i in kwargs]))))

    async def post(self, parameter, **kwargs):
        return json.loads(
            await botsdk.util.HttpRequest.post(
                self.url + parameter["path"], kwargs))
