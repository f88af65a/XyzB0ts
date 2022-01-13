from botsdk.BotModule.Request import Request


class KaiheilaRequest(Request):
    # needOverRide
    # 获取角色
    async def getRoles(self):
        roles = self.getBot().getRoles()
        if self["target_id"] not in roles:
            re = await self.getBot().getServerRoles(
                self["target_id"])["data"]["items"]
            roles = {}
            for i in re:
                roles[re["role_id"]] = i
            self.getBot().addToRoles(self["target_id"], roles)
        else:
            roles = roles[self["target_id"]]
        re = set()
        for i in range(len(self["extra"]["author"]["roles"])):
            if i not in roles:
                re = await self.getBot().getServerRoles(
                    self["target_id"])["data"]["items"]
                roles = {}
                for i in re:
                    roles[re["role_id"]] = i
                self.getBot().addToRoles(self["target_id"], roles)
            re.add(roles[i]["name"])

    # 获取发送者的BotId
    def getUserId(self):
        return f"""Kaiheila:User:{self["author_id"]}"""

    # 获取来源BotId
    def getId(self):
        if self["channel_type"] == "GROUP":
            return ("""Kaiheila:Group:"""
                    f"""{self["extra"]["guild_id"]}:{self["target_id"]}""")
        elif self["channel_type"] == "PERSON":
            return f"""Kaiheila:User:{self["target_id"]}"""

    # 获取消息的首串文本消息
    def getFirstText(self):
        if self["type"] == 1:
            return self["content"]
        else:
            return ""

    # 发送消息
    async def sendMessage(self, messageChain):
        ids = self.getId().split(":")
        sendMethod = None
        if ids[1] == "Group":
            sendMethod = self.getBot().sendGroupMessage
            targetId = ids[3]
        if sendMethod is None:
            return
        if type(messageChain) == str:
            await sendMethod(target_id=targetId, content=messageChain)
        else:
            for i in messageChain.getData():
                if i["type"] == 1:
                    await sendMethod(target_id=targetId, content=i["content"])

    # 获取消息类型
    def getType(self):
        return f"""{self["channel_type"]}:{self["type"]}"""
