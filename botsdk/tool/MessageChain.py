import uuid
import copy
class MessageChain:
    def __init__(self, rhs = None):
        if rhs == None:
            self.data = list()
        elif type(rhs) == list:
            self.data = copy.deepcopy(rhs)
        else:
            self.data = copy.deepcopy(rhs.getData())

    def __add__(self, rhs):
        return MessageChain(self.getData() + rhs.getData())

    def text(self, data : str):
        self.data += [{"type":"Plain","text":data}]
        return self

    def image(self, url: str = None, path: str = None):
        if url is not None:
            self.data += [{"type": "Image", "url":url}]
        elif path is not None:
            #self.data += [{"type": "Image","imageId":"{{{}}}.mirai".format(uuid.uuid4()),"path":path}]
            self.data += [{"type": "Image","path":path}]
        else:
            raise
        return self

    def getData(self):
        return self.data
