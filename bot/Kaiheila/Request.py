from botsdk.BotModule.Request import Request


class KaiheilaRequest(Request):
    # needOverRide
    # 获取角色
    def getRoles(self):
        pass

    # 获取发送者的BotId
    def getUserId(self):
        pass

    # 获取来源BotId
    def getId(self):
        pass

    # 获取消息的首串文本消息
    def getFirstText(self):
        pass

    # 发送消息
    def sendMessage(self, messageChain):
        pass

    # 获取消息类型
    def getType(self):
        pass
