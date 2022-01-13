from botsdk.BotModule.Request import Request


class KaiheilaRequest(Request):
    # needOverRide
    # 获取角色
    def getRoles(self):
        return set(self["author"]["roles"])

    # 获取发送者的BotId
    def getUserId(self):
        return f"""Kaiheila:User:{self["author_id"]}"""

    # 获取来源BotId
    def getId(self):
        if self["channel_type"] == "GROUP":
            return ("""Kaiheila:Group:"""
                    f"""{self["extra"]}:{self["extra"]["guild_id"]}""")
        else:
            return (f"""Kaiheila:User:"""
                    f"""{self["extra"]}:{self["extra"]["guild_id"]}""")

    # 获取消息的首串文本消息
    def getFirstText(self):
        if self["type"] == 1:
            return self["extra"]["content"]
        else:
            return ""

    # 发送消息
    def sendMessage(self, messageChain):
        pass

    # 获取消息类型
    def getType(self):
        return f"""{self["channel_type"]}:{self["type"]}"""
