import asyncio
import struct
from botsdk.util.BotPlugin import BotPlugin


def ParseByte(data, byteSize: int = 1):
    if len(data) < byteSize:
        raise Exception("ParseByteError")
    retByte = data[:byteSize]
    data = data[byteSize:]
    return retByte, data


def ParseString(data):
    for i in range(len(data)):
        if data[i] == 0:
            retData = data[:i]
            data = data[i + 1:]
            return retData, data
    raise Exception("ParseStringError")


def ParseA2SINFO(data: bytes) -> dict:
    ret = dict()
    _, data = ParseByte(data, 4)
    ret["Header"], data = ParseByte(data)
    ret["Header"] = ret["Header"][0]
    ret["Protocol"], data = ParseByte(data)
    ret["Protocol"] = ret["Protocol"][0]
    ret["Name"], data = ParseString(data)
    ret["Name"] = ret["Name"].decode()
    ret["Map"], data = ParseString(data)
    ret["Map"] = ret["Map"].decode()
    ret["Folder"], data = ParseString(data)
    ret["Folder"] = ret["Folder"].decode()
    ret["Game"], data = ParseString(data)
    ret["Game"] = ret["Game"].decode()
    ret["ID"], data = ParseByte(data, 2)
    ret["ID"] = int.from_bytes(ret["ID"], "big")
    ret["Players"], data = ParseByte(data)
    ret["Players"] = ret["Players"][0]
    ret["MaxPlayers"], data = ParseByte(data)
    ret["MaxPlayers"] = ret["MaxPlayers"][0]
    ret["Bots"], data = ParseByte(data)
    ret["Bots"] = ret["Bots"][0]
    ret["Servertype"], data = ParseByte(data)
    ret["Servertype"] = ret["Servertype"][0]
    if ret["Servertype"] == ord('d'):
        ret["Servertype"] = "dedicated server"
    elif ret["Servertype"] == ord('l'):
        ret["Servertype"] = "non-dedicated server"
    else:
        ret["Servertype"] = "SourceTV relay (proxy)"
    ret["Environment"], data = ParseByte(data)
    ret["Environment"] = ret["Environment"][0]
    if ret["Environment"] == ord('l'):
        ret["Environment"] = "Linux"
    elif ret["Environment"] == ord('w'):
        ret["Environment"] = "Windows"
    else:
        ret["Environment"] = "Mac"
    ret["Visibility"], data = ParseByte(data)
    ret["Visibility"] = ret["Visibility"][0]
    if ret["Visibility"] == 0:
        ret["Visibility"] = "public"
    else:
        ret["Visibility"] = "private"
    ret["VAC"], data = ParseByte(data)
    ret["VAC"] = ret["VAC"][0]
    if ret["VAC"] == 0:
        ret["VAC"] = "unsecured"
    else:
        ret["VAC"] = "secured"
    ret["Version"], data = ParseString(data)
    ret["Version"] = ret["Version"].decode()
    ret["EDF"], data = ParseByte(data)
    ret["EDF"] = ret["EDF"][0]
    if ret["EDF"] & 0x80:
        ret["Port"], data = ParseByte(data, 2)
        ret["Port"] = int.from_bytes(ret["Port"], "big")
    if ret["EDF"] & 0x10:
        ret["SteamID"], data = ParseByte(data, 8)
        ret["SteamID"] = int.from_bytes(ret["SteamID"], "big")
    if ret["EDF"] & 0x40:
        ret["SourceTVName"], data = ParseString(data)
        ret["SourceTVName"] = ret["SourceTVName"].decode()
    if ret["EDF"] & 0x20:
        ret["Keywords"], data = ParseString(data)
        ret["Keywords"] = ret["Keywords"].decode()
    if ret["EDF"] & 0x01:
        ret["GameID"], data = ParseByte(data, 8)
        ret["GameID"] = int.from_bytes(ret["GameID"], "big")
    return ret


def ParseA2SPLAYER(data: bytes) -> dict:
    ret = dict()
    _, data = ParseByte(data, 4)
    ret["Header"], data = ParseByte(data)
    ret["Header"] = ret["Header"][0]
    ret["Players"], data = ParseByte(data)
    ret["Players"] = ret["Players"][0]
    ret["PlayerList"] = []
    for i in range(ret["Players"]):
        Index, data = ParseByte(data)
        Index = Index[0]
        Name, data = ParseString(data)
        Name = Name.decode()
        Score, data = ParseByte(data, 4)
        Score = int.from_bytes(Score, "big")
        Duration, data = ParseByte(data, 4)
        Duration = struct.unpack('f', Duration)[0]
        ret["PlayerList"].append(
            [
                Index,
                Name,
                Score,
                Duration
            ]
        )
    return ret


A2S_REQUEST = {
    "INFO": (
        b"\xFF\xFF\xFF\xFF\x54\x53\x6F\x75\x72\x63\x65\x20"
        b"\x45\x6E\x67\x69\x6E\x65\x20\x51\x75\x65\x72\x79\x00"
    ),
    "PLAYER": (
        b"\xFF\xFF\xFF\xFF\x55\x00\x00\x00\x00"
    )
}


class A2SProtocol(asyncio.DatagramProtocol):
    def __init__(self, loop, request, A2SType):
        self.loop = loop
        self.request = request
        self.A2SType = A2SType
        if A2SType == "INFO":
            self.nextStep = self.A2S_INFO_RECV
        elif A2SType == "PLAYER":
            self.nextStep = self.A2S_PLAYER_RECV

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(A2S_REQUEST[self.A2SType])

    def datagram_received(self, data, addr):
        if self.nextStep:
            self.nextStep = self.nextStep(data)
        if not self.nextStep:
            self.transport.close()

    def A2S_INFO_RECV(self, data: bytes):
        if data.startswith(b"\xff\xff\xff\xff\x41"):
            self.transport.sendto(
                A2S_REQUEST["INFO"] + data[5:]
            )
            return self.A2S_INFO_RECV
        try:
            retDict = ParseA2SINFO(data)
            retList = [[i, retDict[i]] for i in retDict]
            ret = "\n".join([f"{i[0]}: {i[1]}" for i in retList])
        except Exception:
            ret = "解析失败"
        self.transport.close()
        asyncio.run_coroutine_threadsafe(
            self.request.send(
                ret
            ),
            self.loop
        )

    def A2S_PLAYER_RECV(self, data: bytes):
        if data.startswith(b"\xff\xff\xff\xff\x41"):
            self.transport.sendto(
                A2S_REQUEST["PLAYER"][:5] + data[5:]
            )
            return self.A2S_PLAYER_RECV
        try:
            retDict = ParseA2SPLAYER(data)
            ret = (
                f'''Header:{retDict["Header"]}\n''' +
                f'''Players:{retDict["Players"]}\n''' +
                "PlayerList:\n" +
                "\n".join(
                    [
                        f"{i[0]} {i[1]} {i[2]} {i[3]}"
                        for i in retDict["PlayerList"]
                    ]
                )
            )
        except Exception:
            ret = "解析失败"
        self.transport.close()
        asyncio.run_coroutine_threadsafe(
            self.request.send(
                ret
            ),
            self.loop
        )

    def connection_lost(self, exc):
        pass


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "steamA2S"
        self.addTarget("GroupMessage", "a2s", self.a2s)
        self.addTarget("GROUP:9", "a2s", self.a2s)
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")

    async def a2s(self, request):
        "a2s [TYPE] [IP:PORT]"
        data = request.getFirstTextSplit()
        if len(data) < 3:
            await request.send(self.a2s.__doc__ + "\n" + " ".join(
                list(A2S_REQUEST.keys())
                )
            )
            return
        if data[1] not in A2S_REQUEST:
            await request.send(
                "错误的TYPE\n" + self.a2s.__doc__ + "\n" + " ".join(
                    list(A2S_REQUEST.keys())
                )
            )
            return
        try:
            ip, port = data[2].split(":")
            port = int(port)
        except Exception:
            await request.send(
                "错误的IP:PORT"
            )
            return
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: A2SProtocol(
                loop,
                request,
                data[1]
            ),
            remote_addr=(ip, port)
        )

        def timeOutClose():
            if not transport.is_closing():
                transport.close()
                asyncio.run_coroutine_threadsafe(
                    request.send("响应超时"),
                    loop
                )
        loop.call_later(
            5,
            timeOutClose
        )


def handle():
    return plugin()
