import asyncio
import time

from botsdk.BotModule.Bot import Bot
from botsdk.util.Error import debugPrint


class KaiheilaBot(Bot):
    # needOverRide
    def init(self):
        self.canDetach = False
        self.stateMap = {
            0: self.getGatewayState,
            1: self.connWsState,
            2: self.waitHelloState,
            3: self.connectedState
        }
        self.state = 0
        self.initFlag()

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
        debugPrint(self.getBotNmae() + "获取gateway中")
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
        debugPrint(self.getBotNmae() + "连接gateway中")
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
        debugPrint(self.getBotNmae() + "等待Hello中")
        re = await self.adapter.wsRecv(timeout=6)
        if re is None or re["s"] != 1 or re["d"]["code"] != 0:
            debugPrint(re)
            await self.adapter.wsDisconnect()
            self.state = 1
        else:
            self.sessionId = re["d"]["session_id"]
            self.state = 3
            debugPrint(self.getBotNmae() + "连接成功")
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

    async def sendGroupMessage(
            self, targetId: str, content: str, type: int = 1,
            quote: str = None, nonce: str = None,
            tempTargetId: str = None):
        return self.adapter.messagecreate(
            type=type, target_id=targetId, content=content,
            quote=quote, nonce=nonce, temp_target_id=tempTargetId
        )