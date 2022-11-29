import asyncio
import time

import ujson as json

from botsdk.BotModule.Bot import Bot
from botsdk.util.Error import debugPrint


class KaiheilaBot(Bot):
    # needOverRide
    def init(self):
        self.stateMap = {
            0: self.getGatewayState,
            1: self.connWsState,
            2: self.waitHelloState,
            3: self.connectedState
        }
        self.state = 0
        self.initFlag()
        self.data["roles"] = {}

    def addToRoles(self, serverId, roles):
        self.data["roles"][serverId] = roles

    def initFlag(self):
        self.sn = None
        self.maxSn = None
        self.dataCache = dict()
        self.lastPingTime = None
        self.getPong = None
        self.lostPong = 0

    async def getGateway(self):
        return await self.adapter.getGateway()

    def destroy(self):
        pass

    async def login(self):
        return 0

    async def logout(self):
        self.adapter.wsDisconnect()

    async def fetchMessage(self):
        return await self.stateMap[self.state]()

    async def getGatewayState(self):
        debugPrint(self.getBotName() + "获取gateway中")
        retry = 0
        while True:
            gateway = await self.getGateway()
            if gateway["code"] != 0:
                debugPrint(gateway["message"])
                retry += 1
                await asyncio.sleep(min(1 << retry, 60))
                continue
            self.gateway = gateway["data"]["url"]
            self.state = 1
            return (0, [])

    async def connWsState(self):
        debugPrint(self.getBotName() + "连接gateway中")
        retry = 0
        while True:
            if await self.adapter.wsConnect(self.gateway) is None:
                retry += 1
                if retry == 2:
                    self.state = 0
                    return (0, [])
                else:
                    await asyncio.sleep(1 << retry)
                    continue
            self.state = 2
            return (0, [])

    async def waitHelloState(self):
        debugPrint(self.getBotName() + "等待Hello中")
        re = await self.adapter.wsRecv(timeout=6)
        if re is None or re["s"] != 1 or re["d"]["code"] != 0:
            debugPrint(re)
            await self.adapter.wsDisconnect()
            self.state = 0
        else:
            self.sessionId = re["d"]["session_id"]
            self.state = 3
            debugPrint(self.getBotName() + "连接成功")
            self.data["me"] = (await self.adapter.userme())["data"]
        return (0, [])

    async def connectedState(self):
        thisTime = time.time()
        if self.lastPingTime is None or thisTime - self.lastPingTime >= 30:
            await self.adapter.wsSend({"s": 2, "sn": self.maxSn})
            self.lastPingTime = thisTime
            self.getPong = False
        if (thisTime - self.lastPingTime >= 6
                and (self.getPong is None or self.getPong is False)):
            self.lostPong += 1
            await asyncio.sleep(1 << self.lostPong)
            if self.lostPong == 2:
                self.initFlag()
                self.state = 1
                return (0, [])
            await self.adapter.wsSend({"s": 2, "sn": self.maxSn})
            self.lastPingTime = time.time()
        data = await self.adapter.wsRecv(timeout=1)
        if data is None:
            return (0, [])
        if data["s"] == 0:
            if self.maxSn is None:
                self.maxSn = data["sn"]
            else:
                self.maxSn = max(self.maxSn, data["sn"])
            self.dataCache[data["sn"]] = data["d"]
            if self.sn is None:
                self.sn = data["sn"]
            if self.sn in self.dataCache:
                reData = self.dataCache[self.sn]
                del self.dataCache[self.sn]
                self.sn += 1
                return (0, [reData])
        elif data["s"] == 3:
            self.getPong = True
            self.lostPong = 0
        elif data["s"] == 5:
            debugPrint(data["d"])
            self.initFlag()
            await self.adapter.wsClose()
            self.state = 0
        elif data["s"] == 6:
            debugPrint("暂时没打算支持这功能")
        return (0, [])

    async def sendGroupMessage(self, type: int = 1, **kwargs):
        return await self.adapter.messagecreate(type=type, **kwargs)

    async def sendFriendMessage(self, type: int = 1, **kwargs):
        return await self.adapter.directmessagecreate(type=type, **kwargs)

    async def getServerRoles(self, serverId):
        return await self.adapter.guildrolelist(guild_id=serverId)

    async def channelView(self, channelId):
        return await self.adapter.channelview(target_id=channelId)

    async def sendMessage(
            self, messageChain, request=None, id=None,
            messageType=None):
        if id is None:
            ids = request.getId().split(":")
        else:
            ids = id.split(":")
        sendMethod = None
        targetId = ids[-1]
        if ids[-2] == "Group":
            sendMethod = self.sendGroupMessage
        elif ids[-2] == "User":
            sendMethod = self.sendFriendMessage
        if sendMethod is None:
            return
        if type(messageChain) == str:
            return await sendMethod(
                type=10,
                target_id=targetId,
                content=json.dumps([
                    {
                        "type": "card",
                        "theme": "secondary",
                        "size": "lg",
                        "modules": [{
                            "type": "section",
                            "text": {
                                "type": "plain-text",
                                "content": messageChain
                            }
                        }]
                    }
                ]
                ))
        else:
            return await sendMethod(
                type=10, target_id=targetId,
                content=json.dumps(
                    [
                        {
                            "type": "card",
                            "theme": "secondary",
                            "size": "lg",
                            "modules": messageChain.getData()
                        }
                    ]
                )
            )

    async def filter(self, request):
        return not (self.data["me"]["id"] == request["author_id"])

    async def guildview(self, serverId):
        return await self.adapter.guildview(guild_id=serverId)
