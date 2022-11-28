from botsdk.BotModule.Request import Request
from botsdk.util.Cookie import AsyncGetCookie, AsyncSetCookie


class KaiheilaRequest(Request):
    def init(self):
        self.messageType = {
            "GROUP"
        }
        self.signalMessage = {
            "PERSON"
        }

    # needOverRide
    # 获取角色
    async def getRoles(self):
        return {str(i) for i in self["extra"]["author"]["roles"]}

    # 获取发送者的BotId
    def getUserId(self):
        return self.userFormat(self["author_id"])

    # 获取来源BotId
    def getId(self):
        if self["channel_type"] == "GROUP":
            return (
                self.getBot().getBotName()
                + ":"
                + self.groupFormat(self["target_id"])
            )
        elif self["channel_type"] == "PERSON":
            return (
                self.getBot().getBotName()
                + ":"
                + self.getUserId()
                )

    # 获取消息的首串文本消息
    def getFirstText(self):
        if self["type"] == 9:
            return self['extra']['kmarkdown']["raw_content"]
        else:
            return ""

    def setFirstText(self, s):
        if self["type"] == 1:
            self['extra']['kmarkdown']["raw_content"] = s

    # 获取消息类型
    def getType(self):
        return f"""{self["channel_type"]}:{self["type"]}"""

    def isSingle(self):
        return self["channel_type"] in self.signalMessage

    def isMessage(self):
        return self["channel_type"] in self.messageType

    async def isGroupOwner(self):
        serverData = await AsyncGetCookie(
            "System:Kook:Server",
            self.getServerId()
        )
        if serverData is None:
            serverData = await self.getBot().guildview(self.getServerId())
            if serverData is None:
                return False
            serverData = serverData["data"]
            await AsyncSetCookie(
                "System:Kook:Server",
                self.getServerId(),
                serverData
            )
        return serverData["user_id"] == self["author_id"]

    # util
    def getServerId(self):
        return self["extra"]["guild_id"]
