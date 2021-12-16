import json

import botsdk.util.HttpRequest
from botsdk.util.Adapter import getAdapter
from botsdk.util.BotException import BotException
from botsdk.util.Error import debugPrint, exceptionExit
from botsdk.util.MessageChain import MessageChain


class Bot:
    def __init__(self, path, port, qq, adapterName, sessionKey=None):
        self.url = f"http://{path}:{port}"
        self.path = path
        self.port = port
        self.qq = qq
        self.adapterName = adapterName
        self.adapter = getAdapter(adapterName, self.url)
        if sessionKey is not None:
            self.sessionKey = sessionKey

    # 非API

    def getData(self):
        return (self.path, self.port, self.qq,
                self.adapterName, self.sessionKey)

    def getQq(self):
        return self.qq

    def getPath(self):
        return self.path

    def getPort(self):
        return self.port

    async def sendMessageById(
            self, id: str, messageChain: MessageChain, quote=None):
        messageType, target = id.split(":")
        target = int(target)
        if messageType == "User":
            await self.sendFriendMessage(target, messageChain.getData(), quote)
        elif messageType == "Group":
            await self.sendGroupMessage(target, messageChain.getData(), quote)
        else:
            raise BotException("Bot.sendMessageById遇到了不支持的类型")

    async def post(self, path, data):
        return json.loads(
            await botsdk.util.HttpRequest.post(self.url + path, data))

    async def get(self, path):
        return json.loads(await botsdk.util.HttpRequest.get(self.url + path))

    async def login(self, qq: int, authkey: str):
        if await self.verify(authkey) is None:
            return 1
        if await self.bind(qq) is None:
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
        # re = await self.post("/release", kv)
        re = await self.adapter.release(kv)
        return re

    async def sendGroupMessage(
            self, target: int, messageChain: list, quote=None):
        '''
        return await self.post(
            "/sendGroupMessage",
            {"sessionKey": self.sessionKey,
                "target": target, "messageChain": messageChain}
            | ({"quote": int(quote)} if quote is not None else {}))
        '''
        return await self.adapter.sendGroupMessage(
            sessionKey=self.sessionKey,
            target=target,
            messageChain=messageChain,
            quote=quote
        )

    async def sendFriendMessage(
            self, target: int, messageChain: list, quote=None):
        '''
        return await self.post(
            "/sendFriendMessage",
            {"sessionKey": self.sessionKey, "target": target,
                "messageChain": messageChain}
            | ({"quote": int(quote)} if quote is not None else {}))
        '''
        return await self.adapter.sendFriendMessage(
            sessionKey=self.sessionKey,
            target=target,
            messageChain=messageChain,
            quote=quote
        )

    async def sendTempMessage(
            self, targetGroup: int, targetQq: int,
            messageChain: list, quote=None):
        '''
        return await self.post(
            "/sendFriendMessage",
            {"sessionKey": self.sessionKey, "qq": targetQq,
                "group": targetGroup, "messageChain": messageChain}
            | ({"quote": int(quote)} if quote is not None else {}))
        '''
        return await self.adapter.sendTempMessage(
            sessionKey=self.sessionKey,
            qq=targetQq,
            group=targetGroup,
            messageChain=messageChain,
            quote=quote
        )

    async def sendNudge(self, target: int, subject: int, kind: str):
        return await self.post(
            "/sendNudge",
            {"sessionKey": self.sessionKey, "target": target,
                "subject": subject, "kind": kind})

    async def recall(self, target: int):
        return await self.post(
            "/recall",
            {"sessionKey": self.sessionKey, "target": target})

    async def fetchMessage(self, count: int):
        '''
        return await self.get("/fetchMessage?sessionKey="
                              + self.sessionKey + "&count=" + str(count))
        '''
        return await self.adapter.fetchMessage(
            sessionKey=self.sessionKey,
            count=count
        )

    async def countMessage(self):
        return await self.get("/countMessage?sessionKey=" + self.sessionKey)

    async def memberList(self, target: int):
        return await self.get("/memberList?sessionKey="
                              + self.sessionKey + "&target=" + str(target))

    async def mute(self, target, memberid, time):
        await self.post(
            "/mute",
            {"sessionKey": self.sessionKey, "target": int(target),
                "memberId": int(memberid), "time": int(time)})

    async def unmute(self, target, memberid):
        await self.post(
            "/unmute",
            {"sessionKey": self.sessionKey, "target": int(target),
                "memberId": int(memberid)})

    async def messageFromId(self, messageId):
        return await self.get("/messageFromId?sessionKey={}&id={}"
                              .format(self.sessionKey, messageId))

    async def doGroupInvite(self, data):
        data.update({"sessionKey": self.sessionKey})
        await self.post("/resp/botInvitedJoinGroupRequestEvent", data)
