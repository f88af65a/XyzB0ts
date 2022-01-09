import asyncio
import socket

from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "unturnedPlayerSize"
        self.addTarget("GroupMessage", "un", self.unSearch)
        self.canDetach = True

    async def unSearch(self, request):
        "/un 服务器ip [端口默认27015]"
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.sendMessage(self.unSearch.__doc__)
            return
        searchData = (b"\xFF\xFF\xFF\xFF\x54\x53\x6F\x75\x72\x63\x65\x20"
                      b"\x45\x6E\x67\x69\x6E\x65\x20\x51\x75\x65\x72\x79\x00")
        loop = asyncio.get_event_loop()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0)
            serIp, serPort = data[1], 27015
            if len(data) == 3:
                try:
                    serPort = int(data[2])
                except Exception:
                    await request.sendMessage("端口应为数字")
                    return
            try:
                await loop.sock_connect(sock, (serIp, int(serPort)))
            except Exception:
                await request.sendMessage("连接失败")
                return
            try:
                await loop.sock_sendall(sock, searchData)
            except Exception:
                await request.sendMessage("发送失败")
                return
            re = None
            try:
                re = await loop.sock_recv(sock, 1501)
            except Exception:
                await request.sendMessage("获取失败")
                return
            if re[0:5] == b"\xff\xff\xff\xff\x41":
                key = re[5:len(re)]
                await loop.sock_sendall(sock, searchData + key)
            re = await loop.sock_recv(sock, 1501)
            re = re[6:]
            serName = ""
            serMap = ""
            serSize = 0
            serMaxSize = 0
            try:
                for i in range(0, len(re)):
                    if re[i] == 0:
                        serName = re[0:i].decode()
                        re = re[i + 1:]
                        break
                    if i == len(re) - 1:
                        raise
                for i in range(0, len(re)):
                    if re[i] == 0:
                        serMap = re[0:i].decode()
                        re = re[i + 1:]
                        break
                    if i == len(re) - 1:
                        raise
                for i in range(0, len(re)):
                    if re[i] == 0:
                        re = re[i + 1:]
                        break
                    if i == len(re) - 1:
                        raise
                for i in range(0, len(re)):
                    if re[i] == 0:
                        re = re[i + 1:]
                        break
                    if i == len(re) - 1:
                        raise
                re = re[2:]
                serSize = str(int(re[0]))
                serMaxSize = str(int(re[1]))
            except Exception:
                await request.sendMessage("解析出错")
                return
            await request.sendMessage(
                    "服务器名:{0}\n服务器地图:{1}\n服务器人数:{2}/{3}".format(
                        serName, serMap, serSize, serMaxSize))


def handle():
    return plugin()
