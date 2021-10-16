import botsdk.tool.HttpRequest
from botsdk.tool.Error import debugPrint,exceptionExit
import json

class Bot:
    def __init__(self, path, port, sessionKey = None):
        self.url = f"http://{path}:{port}"
        self.path = path
        self.port = port
        if sessionKey != None:
            self.sessionKey = sessionKey

    def getPath(self):
        return self.path
    
    def getPort(self):
        return self.port

    async def post(self, path, data):
        return json.loads(await botsdk.tool.HttpRequest.post(self.url + path, data))

    async def get(self, path):
        return json.loads(await botsdk.tool.HttpRequest.get(self.url + path))

    async def login(self, qq:int, authkey:str):
        if await self.verify(authkey) is None:
            return 1
        if await self.bind(qq) is None:
            return 2
        return 0

    async def verify(self, authkey:str):
        kv = dict()
        kv["verifyKey"] = authkey
        re = await self.post("/verify", kv)
        if re is None:
            debugPrint("账号验证失败")
            return None
        if re["code"] == 0:
            self.sessionKey = re["session"]
        else:
            exceptionExit("账号验证失败")
        return re

    async def bind(self, qq:int):
        kv = dict()
        kv["sessionKey"] = self.sessionKey
        kv["qq"] = qq
        re = await self.post("/bind", kv)
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
        re = await self.post("/release", kv)
        return re

    async def sendMessage(self, uid, messageChain: list):
        if ":" in uid:
            await self.sendGroupMessage(int(uid.split(":")[1]), messageChain)
        else:
            await self.sendGroupMessage(int(uid), messageChain)

    async def sendGroupMessage(self, target:int, messageChain:list):
        return await self.post("/sendGroupMessage", {"sessionKey":self.sessionKey, "target":target, "messageChain":messageChain})

    async def sendFriendMessage(self, target:int, messageChain:list):
        return await self.post("/sendFriendMessage", {"sessionKey":self.sessionKey, "target":target, "messageChain":messageChain})

    async def fetchMessage(self, count:int):
        return await self.get("/fetchMessage?sessionKey=" + self.sessionKey + "&count=" + str(count))

    async def countMessage(self):
        return await self.get("/countMessage?sessionKey=" + self.sessionKey)

    async def memberList(self, target:int):
        return await self.get("/memberList?sessionKey=" + self.sessionKey + "&target=" + str(target))

    async def mute(self, target, memberid, time):
        await self.post("/mute", {"sessionKey":self.sessionKey, "target":int(target), "memberId":int(memberid), "time":int(time)})

    async def unmute(self, target, memberid):
        await self.post("/unmute", {"sessionKey":self.sessionKey, "target":int(target), "memberId":int(memberid)})

    async def messageFromId(self, messageId):
        return await self.get("/messageFromId?sessionKey={}&id={}".format(self.sessionKey, messageId))

    async def doGroupInvite(self, data):
        data.update({"sessionKey":self.sessionKey})
        await self.post("/resp/botInvitedJoinGroupRequestEvent", data)
