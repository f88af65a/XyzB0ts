from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Permission import roleCheck


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "MiraiBotControl"
        self.addTarget("GroupMessage", "quitGroup", self.quitGroup)
        self.addTarget("GroupMessage", "listGroup", self.listGroup)
        self.addTarget("GroupMessage", "listFriend", self.listFriend)
        self.addTarget("GroupMessage", "chatWithGroup", self.chatWithGroup)
        self.addTarget("GroupMessage", "chatWithFriend", self.chatWithFriend)

        self.addTarget("FriendMessage", "quitGroup", self.quitGroup)
        self.addTarget("FriendMessage", "listGroup", self.listGroup)
        self.addTarget("FriendMessage", "listFriend", self.listFriend)
        self.addTarget("FriendMessage", "chatWithGroup", self.chatWithGroup)
        self.addTarget("FriendMessage", "chatWithFriend", self.chatWithFriend)

        self.addType("BotInvitedJoinGroupRequestEvent", self.groupInvite)
        self.addType("NewFriendRequestEvent", self.friendRequest)
        self.addBotType("Mirai")
        self.canDetach = True

    async def groupInvite(self, request):
        await request.getBot().BotInvitedJoinGroupRequestEvent(
            {
                "eventId": request["eventId"],
                "fromId": request["fromId"],
                "groupId": request["groupId"],
                "operate":
                    (0 if await roleCheck(request, {"Inviter"}) else 1),
                "message": ""
            }
        )

    async def friendRequest(self, request):
        await request.getBot().NewFriendRequestEvent(
            {
                "eventId": request["eventId"],
                "fromId": request["fromId"],
                "groupId": request["groupId"],
                "operate":
                    (0 if await roleCheck(request, {"Inviter"}) else 1),
                "message": ""
            }
        )

    async def quitGroup(self, request):
        '''quitGroup q群 #退出q群'''
        ret = await request.getBot().quit(request.getFirstTextSplit()[1])
        await request.sendMessage(f"退出完成 响应{ret}")

    async def listGroup(self, request):
        '''listGroup #打印所有群聊'''
        ret = await request.getBot().groupList()
        if ret["code"] != 0:
            request.sendMessage("请求失败")
            return
        ret = ret["data"]
        data = ""
        for i in range(len(ret)):
            data += (f'''群号:{ret[i]["id"]}\n'''
                     f'''群名:{ret[i]["name"]}\n'''
                     f'''权限:{ret[i]["permission"]}''')
            if i != len(ret) - 1:
                data += "\n------\n"
        await request.sendMessage(data)

    async def listFriend(self, request):
        '''listFriend #打印所有好友'''
        ret = await request.getBot().friendList()
        if ret["code"] != 0:
            request.sendMessage("请求失败")
            return
        ret = ret["data"]
        data = ""
        for i in range(len(ret)):
            data += (f'''Q号:{ret[i]["id"]}\n'''
                     f'''名称:{ret[i]["nickname"]}\n'''
                     f'''备注:{ret[i]["remark"]}''')
            if i != len(ret) - 1:
                data += "\n------\n"
        await request.sendMessage(data)

    async def chatWithGroup(self, request):
        '''chatWithGroup [群号,] 消息'''
        data = request.getFirstTextSplit()
        message = request.getMessageChain()
        if len(message) > 2 and message[1]["type"] == "Quote":
            if len(data) < 2:
                await request.sendMessage(self.chatWithGroup.__doc__)
                return
            bot = request.getBot()
            quoteMessageChain = await bot.messageFromId(message[1]["id"])
            if quoteMessageChain["code"] != 0:
                await request.sendMessage("消息不在缓存中")
                return
            message = quoteMessageChain["data"]["messageChain"][1:]
        else:
            if len(data) < 3:
                await request.sendMessage(self.chatWithGroup.__doc__)
                return
            message = " ".join(data[2:])
        ids = data[1].split(",")
        botName = request.getBot().getBotName()
        for i in ids:
            ret = await request.send(
                    message,
                    id=f"{botName}:QQ:Group:{i}",
                    messageType="GroupMessage"
                    )
            ret = ret["code"]
            await request.send(f'''发送给{i}返回:{"成功" if ret == 0 else "失败"}''')
        await request.send("发送完成")

    async def chatWithFriend(self, request):
        data = request.getFirstTextSplit()
        message = request.getMessageChain()
        if len(message) > 2 and message[1]["type"] == "Quote":
            if len(data) < 2:
                await request.sendMessage(self.chatWithGroup.__doc__)
                return
            bot = request.getBot()
            quoteMessageChain = await bot.messageFromId(message[1]["id"])
            if quoteMessageChain["code"] != 0:
                await request.sendMessage("消息不在缓存中")
                return
            message = quoteMessageChain["data"]["messageChain"][1:]
        else:
            if len(data) < 3:
                await request.sendMessage(self.chatWithGroup.__doc__)
                return
            message = " ".join(data[2:])
        ids = data[1].split(",")
        botName = request.getBot().getBotName()
        for i in ids:
            ret = await request.send(
                    message,
                    id=f"{botName}:QQ:User:{i}",
                    messageType="FriendMessage"
                    )
            ret = ret["code"]
            await request.send(f'''发送给{i}返回:{"成功" if ret == 0 else "失败"}''')
        await request.send("发送完成")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
