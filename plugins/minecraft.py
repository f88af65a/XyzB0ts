import asyncio
import json
import socket
import time

from botsdk.BotRequest import BotRequest
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Error import printTraceBack
from botsdk.util.MessageChain import MessageChain


def getMcRequestData(ip, port):
    data = (b"\x00\xff\xff\xff\xff\x0f"
            + bytes([len(ip.encode("utf8"))])
            + ip.encode("utf8")
            + int.to_bytes(port, 2, byteorder="big")
            + b"\x01\x01\x00")
    return bytes([len(data) - 2]) + data


def getVarInt(b):
    b = list(b)
    b.reverse()
    ans = 0
    for i in b:
        ans <<= 7
        ans |= (i & 127)
    return ans


class plugin(BotPlugin):
    "/[mcbe/mcpe] ip [端口]"

    def __init__(self):
        super().__init__()
        self.name = "minecraft"
        self.addTarget("GroupMessage", "mc", self.getMc)
        self.addTarget("GroupMessage", "mcbe", self.getBe)
        self.canDetach = True

    async def getMc(self, request: BotRequest):
        "/mc ip [端口]不写默认25565"
        data = request.getFirstTextSplit()
        serverIp = None
        serverPort = 25565
        if len(data) < 2:
            await request.sendMessage(
                MessageChain().plain("缺少参数\n/mc ip [端口]不写默认25565"))
            return
        if len(data) >= 2:
            serverIp = data[1]
        if len(data) == 3:
            if not (data[2].isnumeric()
                    and int(data[2]) >= 0
                    and int(data[2]) <= 65535):
                request.sendMessage(MessageChain().plain("端口有误"))
                return
            serverPort = int(data[2])
        # 初始化socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0)
            loop = asyncio.get_event_loop()
            # 连接
            try:
                await loop.sock_connect(sock, (serverIp, serverPort))
            except Exception:
                await request.sendMessage(MessageChain().plain("连接失败"))
                return
            requestData = getMcRequestData(serverIp, serverPort)
            # 发送
            try:
                await loop.sock_sendall(sock, requestData)
            except Exception:
                await request.sendMessage(MessageChain().plain("请求发送失败"))
                return
            # 接受
            responseData = bytes()
            breakFlag = True
            dataSize = 10000000
            stime = time.time()
            while time.time() - stime <= 2 and breakFlag:
                for i in range(0, len(responseData)):
                    if int(responseData[i]) & 128 == 0:
                        dataSize = getVarInt(responseData[0:i + 1]) + i + 1
                        break
                if len(responseData) == dataSize:
                    breakFlag = False
                    break
                rdata = await loop.sock_recv(sock, 10240)
                if len(rdata) == 0:
                    await request.sendMessage(
                        MessageChain().plain("接受请求时连接断开"))
                    return -1
                responseData += rdata
                await asyncio.sleep(0)
            for i in range(0, len(responseData)):
                if int(responseData[i]) & 128 == 0:
                    responseData = responseData[i + 2:]
                    break
            for i in range(0, len(responseData)):
                if int(responseData[i]) & 128 == 0:
                    responseData = responseData[i + 1:]
                    break
            responseData = json.loads(responseData)
            description = ""
            if "extra" in responseData["description"]:
                for i in responseData["description"]["extra"]:
                    if "text" in i:
                        description += i["text"]
            try:
                printData = "信息:{0}\n版本:{1}\n人数:{2}/{3}".format(
                    description, responseData["version"]["name"],
                    responseData["players"]["online"],
                    responseData["players"]["max"])
                if "playerlist" in data:
                    printData += "\n在线玩家:\n"
                    for i in range(0, len(responseData["players"]["sample"])):
                        printData += responseData
                        ["players"]["sample"][i]["name"]
                        if i != len(responseData["players"]["sample"]) - 1:
                            printData += "\n"
                await request.sendMessage(MessageChain().plain(printData))
            except Exception:
                await request.sendMessage(MessageChain().plain("解析过程中出错"))
                printTraceBack()

    async def getBe(self, request):
        "/mcbe ip [端口]不写默认19132"
        data = request.getFirstTextSplit()
        serverIp = None
        serverPort = 19132
        if len(data) < 2:
            await request.sendMessage(
                MessageChain().plain("缺少参数\n/mcbe ip [端口]不写默认19132"))
            return
        if len(data) >= 2:
            serverIp = data[1]
        if len(data) == 3:
            if not (data[2].isnumeric()
                    and int(data[2]) >= 0
                    and int(data[2]) <= 65535):
                request.sendMessage(MessageChain().plain("端口有误"))
                return
            serverPort = int(data[2])
        # 初始化socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0)
            loop = asyncio.get_event_loop()
            # 连接
            try:
                await loop.sock_connect(sock, (serverIp, serverPort))
            except Exception:
                await request.sendMessage(MessageChain().plain("连接失败"))
                return
            requestData = (b"\x01"
                           + b"\x00" * 8
                           + b"\x00\xff\xff\x00\xfe\xfe\xfe\
                               \xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78"
                           + b"\x00" * 8)
            # 发送
            try:
                await loop.sock_sendall(sock, requestData)
            except Exception:
                await request.sendMessage(MessageChain().plain("请求发送失败"))
                return
            # 接受
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
                    await request.sendMessage(
                        MessageChain().plain("接收过程中连接断开"))
                    return
                breakFlag = False
                await asyncio.sleep(0)
            responseData = responseData[35:].decode()
            responseData = responseData.split(";")
            printData = ""
            try:
                printData += f"服务器名:{responseData[1]}\n"
                printData += f"人数:{responseData[4]}/{responseData[5]}\n"
                printData += f"游戏模式:{responseData[8]}\n"
                printData += (
                    f"版本:{responseData[0]} {responseData[2]} {responseData[3]}"
                    )
                await request.sendMessage(MessageChain().plain(printData))
            except Exception:
                await request.sendMessage(MessageChain().plain("解析过程中出错"))
                printTraceBack()


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
