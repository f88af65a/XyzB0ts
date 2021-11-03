import copy
from botsdk.util.BotException import BotException
from botsdk.util.OutDated import OutDated

class MessageChain:
    def __init__(self, rhs = None):
        if rhs == None:
            self.data = list()
        elif type(rhs) == list:
            self.data = copy.deepcopy(rhs)
        elif type(rhs) == MessageChain:
            self.data = copy.deepcopy(rhs.getData())

    def __add__(self, rhs):
        return MessageChain(copy.deepcopy(self.getData() + rhs.getData()))

    def text(self, data : str):
        return self.plain(data)

    def plain(self, data):
        self.data += [{"type": "Plain", "text": data}]
        return self

    def image(self, imageId: str=None, url: str=None, path: str=None, type: str="GroupMessage"):
        imgData = [{"type": "Image"}]
        if imageId is not None:
            imgData[0]["imageId"] = imageId
        if url is not None:
            imgData[0]["url"] = url
        if path is not None:
            imgData[0]["path"] = path
        else:
            raise BotException("MessageChain.image需要一个正常的参数")
        self.data += imgData
        return self

    def flashImage(self, imageId: str=None, url: str=None, path: str=None, type: str="GroupMessage"):
        imgData = [{"type": "FlashImage"}]
        if imageId is not None:
            imgData[0]["imageId"] = imageId
        if url is not None:
            imgData[0]["url"] = url
        if path is not None:
            imgData[0]["path"] = path
        else:
            raise BotException("MessageChain.image需要一个正常的参数")
        self.data += imgData
        return self

    def at(self, data: str):
        self.data += [{"type":"At", "target":data}]
        return self

    def atAll(self):
        self.data += [{"type":"AtAll"}]
        return self

    def face(self, faceId: int=None, name: str=None):
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
