from botsdk.BotModule.Request import Request


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
        roles = self.getBot().getRoles()
        if self["extra"]["guild_id"] not in roles:
            re = (await self.getBot().getServerRoles(
                self["extra"]["guild_id"]))["data"]["items"]
            roles = {}
            for i in re:
                roles[i["role_id"]] = i
            self.getBot().addToRoles(self["extra"]["guild_id"], roles)
        else:
            roles = roles[self["extra"]["guild_id"]]
        ret = set()
        requestRoles = self["extra"]["author"]["roles"]
        for i in requestRoles:
            if i not in roles:
                re = (await self.getBot().getServerRoles(
                    self["extra"]["guild_id"]))["data"]["items"]
                roles = {}
                for j in re:
                    roles[j["role_id"]] = j
                self.getBot().addToRoles(self["extra"]["guild_id"], roles)
            ret.add(roles[i]["name"])
        return ret

    # 获取发送者的BotId
    def getUserId(self):
        return self.userFormat(self["author_id"])

    # 获取来源BotId
    def getId(self):
        if self["channel_type"] == "GROUP":
            return self.groupFormat(self["target_id"])
        elif self["channel_type"] == "PERSON":
            return self.userFormat(self["target_id"])

    # 获取消息的首串文本消息
    def getFirstText(self):
        if self["type"] == 1:
            return self["content"]
        else:
            return ""

    def setFirstText(self, s):
        if self["type"] == 1:
            self["content"] = s

    # 获取消息类型
    def getType(self):
        return f"""{self["channel_type"]}:{self["type"]}"""

    def isSingle(self):
        return self["channel_type"] in self.signalMessage

    def isMessage(self):
        return self["channel_type"] in self.messageType
