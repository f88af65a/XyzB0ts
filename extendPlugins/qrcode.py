import uuid
import os
import sys
import qrcode

from botsdk.util.JsonConfig import getConfig
from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "qrcode"
        self.addTarget("GroupMessage", "qrcode", self.makeqrcode)
        self.addBotType("Mirai")

    async def makeqrcode(self, request):
        '''makeqrcode 数据 #生成二维码'''
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.sendMessage(self.makeqrcode.__doc__)
            return
        imageUUID = str(uuid.uuid4())
        qrcode.make(data[1]).save(
            getConfig()["localFilePath"] + f"{imageUUID}"
        )
        messageChain = request.makeMessageChain()
        messageChain.image(
            path=sys.path[0] + "/"
            + getConfig()["localFilePath"] + f"{imageUUID}"
        )
        await request.send(
            messageChain
        )
        os.remove(
            getConfig()["localFilePath"] + f"{imageUUID}"
        )


def handle():
    return plugin()
