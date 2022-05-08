import asyncio
import socket
import time

from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "battlebit"
        self.addTarget("GroupMessage", "bbnews", self.getBBnews)
        self.addTarget("GROUP:9", "bbnews", self.getBBnews)
        self.addTarget("GroupMessage", "bbstate", self.getBBstate)
        self.addTarget("GROUP:9", "bbstate", self.getBBstate)
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.canDetach = True

    async def getBBnews(self, request):
        "/bbnews"
        serverIp = "37.153.157.41"
        serverPort = 29993
        # 初始化socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0)
            loop = asyncio.get_event_loop()
            # 连接
            try:
                await loop.sock_connect(sock, (serverIp, serverPort))
            except Exception:
                await request.sendMessage("连接失败")
                return
            requestData = (b"\x00\x01\x00\x00\x00\x1d\xb9"
                           b"\xf3\xf8\xf0\x29\xd6\x49\xa9")
            # 发送
            try:
                await loop.sock_sendall(sock, requestData)
            except Exception:
                await request.sendMessage("请求发送失败")
                return
            # 接受1
            responseData = bytes()
            breakFlag = True
            stime = time.time()
            while time.time() - stime <= 2 and breakFlag:
                try:
                    responseData = await loop.sock_recv(sock, 10240)
                except Exception:
                    responseData = b""
                if len(responseData) == 0:
                    sock.close()
                    await request.sendMessage("接收过程中连接断开")
                    return
                breakFlag = False
                await asyncio.sleep(0)
            if responseData != b"\x01\x00\x00":
                await request.sendMessage("响应接受失败")
                return
            # 接受2
            responseData = bytes()
            breakFlag = True
            stime = time.time()
            while time.time() - stime <= 2 and breakFlag:
                try:
                    responseData = await loop.sock_recv(sock, 10240)
                except Exception:
                    responseData = b""
                if len(responseData) == 0:
                    sock.close()
                    await request.sendMessage("接收过程中连接断开")
                    return
                breakFlag = False
                await asyncio.sleep(0)
            # 发送响应
            try:
                await loop.sock_sendall(sock, b"\x01\x00\x00")
            except Exception:
                await request.sendMessage("响应发送失败")
                return
            printData = responseData[8:].decode("utf8", "ignore")
            await request.sendMessage(printData)

    async def getBBstate(self, request):
        "/bbnews"
        serverIp = "37.153.157.41"
        serverPort = 29993
        # 初始化socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0)
            loop = asyncio.get_event_loop()
            # 连接
            try:
                await loop.sock_connect(sock, (serverIp, serverPort))
            except Exception:
                await request.sendMessage("连接失败")
                return
            requestData = (b"\x00\x01\x00\x00\x00\x05\xb9"
                           b"\xf3\xf8\xf0\x29\xd6\x49\xa9")
            # 发送请求
            try:
                await loop.sock_sendall(sock, requestData)
            except Exception:
                await request.sendMessage("请求发送失败")
                return
            # 接受通用响应
            responseData = bytes()
            breakFlag = True
            stime = time.time()
            while time.time() - stime <= 2 and breakFlag:
                try:
                    responseData = await loop.sock_recv(sock, 10240)
                except Exception:
                    responseData = b""
                if len(responseData) == 0:
                    sock.close()
                    await request.sendMessage("接收过程中连接断开")
                    return
                breakFlag = False
                await asyncio.sleep(0)
            if responseData != b"\x01\x00\x00":
                await request.sendMessage("响应接受失败")
                return
            # 接受服务器调用
            responseData = bytes()
            breakFlag = True
            stime = time.time()
            while time.time() - stime <= 2 and breakFlag:
                try:
                    responseData = await loop.sock_recv(sock, 10240)
                except Exception:
                    responseData = b""
                if len(responseData) == 0:
                    sock.close()
                    await request.sendMessage("接收过程中连接断开")
                    return
                breakFlag = False
                await asyncio.sleep(0)
            if (len(responseData) == 0 or responseData[:14] != (
                    b"\x00\x01\x00\x00\x00\x01\x00"
                    b"\x18\x07\x74\x70\x19\xda\x08")):
                await request.sendMessage("响应接受失败")
                return
            # 发送响应
            try:
                await loop.sock_sendall(sock, b"\x01\x00\x00")
            except Exception:
                await request.sendMessage("响应发送失败")
                return
            await request.sendMessage(
                "大概率没开" if len(responseData) == 14 else "可能开了")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
