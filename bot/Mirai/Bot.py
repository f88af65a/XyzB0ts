from botsdk.BotModule.Bot import Bot
from botsdk.util.BotException import BotException
from botsdk.util.Error import debugPrint, exceptionExit
from botsdk.BotModule.MessageChain import MessageChain


class MiraiBot(Bot):
    def init(self):
        self.path = self.data["path"]
        self.qq = self.data["qq"]
        if "sessionKey" in self.data:
            self.sessionKey = self.data["sessionKey"]

    # 非API

    def getQq(self):
        return self.qq

    def getPath(self):
        return self.path

    async def sendMessage(
            self, id: str, messageChain: MessageChain, quote=None):
        ids = id.split(":")
        messageType = ids[1]
        target = ids[2]
        target = int(target)
        if type(messageChain) == str:
            messageChain = self.makeMessageChain().text(messageChain)
        if messageType == "User":
            await self.sendFriendMessage(target, messageChain.getData(), quote)
        elif messageType == "Group":
            await self.sendGroupMessage(target, messageChain.getData(), quote)
        else:
            raise BotException("Bot.sendMessage遇到了不支持的类型")

    async def login(self):
        if await self.verify(self.data["passwd"]) is None:
            return 1
        if await self.bind(self.qq) is None:
            return 2
        return 0

    # API

    async def verify(self, authkey: str):
        re = await self.adapter.verify(verifyKey=authkey)
        if re is None:
            debugPrint("账号验证失败")
            return None
        if re["code"] == 0:
            self.sessionKey = re["session"]
            self.data["sessionKey"] = self.sessionKey
        else:
            exceptionExit("账号验证失败")
        return re

    async def bind(self, qq: int):
        re = await self.adapter.bind(
            sessionKey=self.sessionKey, qq=qq)
        if re is None:
            debugPrint("账号绑定失败")
            return None
        if re["code"] == 0:
            self.qq = qq
        return re

    async def release(self):
        kv = dict()
        kv["sessionKey"] = self.sessionKey
        kv["qq"] = int(self.qq)
        re = await self.adapter.release(kv)
        return re

    async def sendGroupMessage(
            self, target: int, messageChain: list, quote=None):
        kw = dict()
        kw["sessionKey"] = self.sessionKey
        kw["target"] = target
        kw["messageChain"] = messageChain
        if quote:
            kw["quote"] = quote
        return await self.adapter.sendGroupMessage(**kw)

    async def sendFriendMessage(
            self, target: int, messageChain: list, quote=None):
        kw = dict()
        kw["sessionKey"] = self.sessionKey
        kw["target"] = target
        kw["messageChain"] = messageChain
        if quote:
            kw["quote"] = quote
        return await self.adapter.sendFriendMessage(**kw)

    async def sendTempMessage(
            self, targetGroup: int, targetQq: int,
            messageChain: list, quote=None):
        return await self.adapter.sendTempMessage(
            sessionKey=self.sessionKey,
            qq=targetQq,
            group=targetGroup,
            messageChain=messageChain,
            quote=quote
        )

    async def sendNudge(self, target: int, subject: int, kind: str):
        return await self.adapter.sendNudge(
            sessionKey=self.sessionKey,
            target=target,
            subject=subject,
            kind=kind
        )

    async def recall(self, target: int):
        return await self.adapter.recall(
            sessionKey=self.sessionKey,
            target=target
        )

    async def fetchMessage(self):
        re = await self.adapter.fetchMessage(
            sessionKey=self.sessionKey,
            count=str(128)
        )
        if re["code"] != 0:
            return (1, re)
        _readList = []
        for i in range(0, len(re["data"])):
            _readList.append(re["data"][i])
        return (0, _readList)

    async def memberList(self, target: int):
        return await self.adapter.memberList(
            sessionKey=self.sessionKey,
            target=target
        )

    async def friendList(self, target: int):
        return await self.adapter.groupList(
            sessionKey=self.sessionKey
        )

    async def groupList(self, target: int):
        return await self.adapter.groupList(
            sessionKey=self.sessionKey
        )

    async def mute(self, target, memberId, time):
        return await self.adapter.mute(
            sessionKey=self.sessionKey,
            target=target,
            memberId=memberId,
            time=time
        )

    async def unmute(self, target, memberId):
        return await self.adapter.unmute(
            sessionKey=self.sessionKey,
            target=target,
            memberId=memberId
        )

    async def messageFromId(self, messageId: int):
        return await self.adapter.messageFromId(
            sessionKey=self.sessionKey,
            id=messageId
        )

    async def MemberJoinRequestEvent(self, data):
        return await self.adapter.BotInvitedJoinGroupRequestEvent(
            sessionKey=self.sessionKey,
            eventId=data["eventId"],
            fromId=data["fromId"],
            groupId=data["groupId"],
            operate=data["operate"],
            message=data["message"]
        )

    async def BotInvitedJoinGroupRequestEvent(self, data):
        return await self.adapter.BotInvitedJoinGroupRequestEvent(
            sessionKey=self.sessionKey,
            eventId=data["eventId"],
            fromId=data["fromId"],
            groupId=data["groupId"],
            operate=data["operate"],
            message=data["message"]
        )

    async def NewFriendRequestEvent(self, data):
        return await self.adapter.NewFriendRequestEvent(
            sessionKey=self.sessionKey,
            eventId=data["eventId"],
            fromId=data["fromId"],
            groupId=data["groupId"],
            operate=data["operate"],
            message=data["message"]
        )
