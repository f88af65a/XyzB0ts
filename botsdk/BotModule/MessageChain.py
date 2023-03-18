import copy


# 对MessageChain功能的基本封装
class MessageChain:
    def __init__(self, rhs=None):
        if rhs is None:
            self.data = list()
        elif type(rhs) == list:
            self.data = copy.deepcopy(rhs)
        elif type(rhs) == MessageChain:
            self.data = copy.deepcopy(rhs.getData())

    def getData(self):
        return self.data

    def __add__(self, rhs):
        return MessageChain(copy.deepcopy(self.getData() + rhs.getData()))

    def text(self, s: str):
        return self.plain(s)

    def plain(self, s: str):
        pass

    def image(self, *args, **kwargs):
        pass

    def add(self, data):
        self.data.append(data)