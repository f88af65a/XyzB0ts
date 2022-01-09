from botsdk.util.BotException import BotException
from botsdk.BotModule.MessageChain import MessageChain


class MiraiMessageChain(MessageChain):
    def __init__(self, rhs=None):
        super().__init__(rhs)

    def plain(self, data):
        self.data += [{"type": "Plain", "text": data}]
        return self

    def image(self, imageId: str = None, url: str = None,
              path: str = None, type: str = "GroupMessage"):
        imgData = [{"type": "Image"}]
        if imageId is not None:
            imgData[0]["imageId"] = imageId
        elif url is not None:
            imgData[0]["url"] = url
        elif path is not None:
            imgData[0]["path"] = path
        else:
            raise BotException("MessageChain.image需要一个正常的参数")
        self.data += imgData
        return self

    def flashImage(self, imageId: str = None, url: str = None,
                   path: str = None, type: str = "GroupMessage"):
        imgData = [{"type": "FlashImage"}]
        if imageId is not None:
            imgData[0]["imageId"] = imageId
        elif url is not None:
            imgData[0]["url"] = url
        elif path is not None:
            imgData[0]["path"] = path
        else:
            raise BotException("MessageChain.image需要一个正常的参数")
        self.data += imgData
        return self

    def at(self, data: str):
        self.data += [{"type": "At", "target": data}]
        return self

    def atAll(self):
        self.data += [{"type": "AtAll"}]
        return self

    def face(self, faceId: int = None, name: str = None):
        faceData = [{"type": "Face"}]
        if faceId is not None:
            faceData[0]["faceId"] = faceId
        if name is not None:
            faceData[0]["name"] = name
        else:
            raise BotException("MessageChain.image需要一个正常的参数")
        self.data += faceData
        return self

    def getData(self):
        return self.data
