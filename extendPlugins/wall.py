from botsdk.util.BotPlugin import BotPlugin
import redis
import base64
import ujson
import time
import hashlib


class plugin(BotPlugin):
    def onLoad(self):
        self.addBotType("Mirai")
        self.name = "wall"
        self.addType("TempMessage", self.fetchMessage)
        self.addType("MemberJoinRequestEvent", self.memberJoin)
        self.addTarget("GroupMessage", "wall.kick", self.kick)
        self.addTarget("FriendMessage", "wall.kick", self.kick)
        self.addTarget("GroupMessage", "wall.recall", self.recall)
        self.addTarget("FriendMessage", "wall.recall", self.recall)
        self.addTarget("GroupMessage", "wall.limit", self.limit)
        self.addTarget("FriendMessage", "wall.limit", self.limit)
        self.addTarget("GroupMessage", "wall.group", self.group)
        self.addTarget("FriendMessage", "wall.group", self.group)
        self.addTarget("GroupMessage", "wall.get", self.get)
        self.addTarget("FriendMessage", "wall.get", self.get)
        self.reChatDict = {}
        self.canDetach = True
        self.sql = redis.Redis(
            host="localhost", port=6379, decode_responses=True, db=4)
        '''
        redis
        消息格式:
        {
            "msgId":[消息号,],
            "sender":"发送者",
            "msg":"消息的base64",
            "time":"消息发送时间"
        }
        涉及的cookie
        wallKick 黑名单
        wallGroup 设为墙的群
        wallLimit cd
        '''

    def getFix(self, N):
        binData = bin(N)[2:]
        zeroCount = 0
        oneCount = 0
        for i in binData:
            if i == '0':
                zeroCount += 1
            else:
                oneCount += 1
        N += zeroCount
        return hashlib.md5(
            base64.b64encode(
                str(N ^ oneCount).encode()
            )
        ).hexdigest()

    async def memberJoin(self, request):
        ret = {}
        ret["eventId"] = request["eventId"]
        ret["fromId"] = request["fromId"]
        ret["groupId"] = request["groupId"]
        ret["operate"] = 0
        ret["message"] = ""
        cookie = request.getCookie("wallKick", id="wall")
        if cookie is None:
            cookie = []
        if request.userFormat(request["fromId"]) in cookie:
            ret["operate"] = 1
            ret["message"] = "黑名单"
        await request.getBot().MemberJoinRequestEvent(ret)

    async def fetchMessage(self, request):
        if not request.isMessage():
            return
        group = request.getCookie("wallGroup", id="wall")
        if group is None:
            group = []
        if request.getId() not in group:
            return
        limit = request.getCookie("wallLimit", id="wall")
        if limit is None:
            limit = {}
        if ((uid := request.getUserId()) in limit
                and time.time() < limit[uid]):
            return
        limit[uid] = time.time() + 30
        request.setCookie("wallLimit", limit, id="wall")
        sqlId = self.sql.incr("msgId")
        sendData = request.getFirstText()
        fixName = self.getFix(int(request.getUserId().split(":")[-1]))
        sendDataFormat = f'''消息id:{sqlId}\n识别码:{fixName}\n{sendData}'''
        msgId = []
        bot = request.getBot()
        for i in group:
            ret = await bot.sendGroupMessage(
                i.split(":")[-1],
                request.makeMessageChain()
                .text(sendDataFormat).getData()
                )
            if ret["code"] == 0:
                msgId.append(ret["messageId"])
        sqlData = {
            "msgId": msgId,
            "sender": request.getUserId(),
            "msg": base64.b64encode(sendData.encode()).decode(),
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }
        self.sql.set(sqlId, ujson.dumps(sqlData))

    async def kick(self, request):
        '''wall.kick add/del q号'''
        data = request.getFirstTextSplit()
        if len(data) != 3:
            await request.sendMessage(self.kick.__doc__)
            return
        cookie = request.getCookie("wallKick", id="wall")
        if cookie is None:
            cookie = []
        group = request.getCookie("wallGroup", id="wall")
        if group is None:
            group = []
        if data[1] == "add":
            if (fmtData := request.userFormat(data[2])) not in cookie:
                cookie.append(fmtData)
                request.setCookie("wallKick", cookie, id="wall")
                bot = request.getBot()
                for i in group:
                    await bot.kick(
                        target=int(i.split(":")[-1]),
                        memberId=data[2])
        elif data[1] == "del":
            if (fmtData := request.userFormat(data[2])) in cookie:
                cookie.remove(fmtData)
                request.setCookie("wallKick", cookie, id="wall")
        else:
            await request.sendMessage("错误的操作")
            return
        await request.sendMessage("修改完成")

    async def recall(self, request):
        '''wall.recall 消息id'''
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.sendMessage(self.recall.__doc__)
            return
        if not self.sql.exists(data[1]):
            await request.sendMessage("消息不存在")
            return
        data = ujson.loads(self.sql.get(data[1]))
        bot = request.getBot()
        for i in data["msgId"]:
            await bot.recall(i)
        await request.sendMessage("撤回完成")

    async def limit(self, request):
        '''wall.limit qq time'''
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.sendMessage(self.limit.__doc__)
            return
        cookie = request.getCookie("wallLimit", id="wall")
        if cookie is None:
            cookie = {}
        uid = request.userFormat(data[1])
        cookie[uid] = time.time() + int(data[2])
        request.setCookie("wallLimit", cookie, id="wall")
        await request.sendMessage("修改完成")

    async def group(self, request):
        '''wall.group add/del 群号'''
        data = request.getFirstTextSplit()
        if len(data) != 3:
            await request.sendMessage(self.group.__doc__)
            return
        cookie = request.getCookie("wallGroup", id="wall")
        if cookie is None:
            cookie = []
        if data[1] == "add":
            if (fmtData := request.groupFormat(data[2])) not in cookie:
                cookie.append(fmtData)
                request.setCookie("wallGroup", cookie, id="wall")
        elif data[1] == "del":
            if (fmtData := request.groupFormat(data[2])) in cookie:
                cookie.remove(fmtData)
                request.setCookie("wallGroup", cookie, id="wall")
        await request.sendMessage("修改完成")

    async def get(self, request):
        '''wall.get 消息id'''
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.sendMessage(self.recall.__doc__)
            return
        if not self.sql.exists(data[1]):
            await request.sendMessage("消息不存在")
            return
        data = ujson.loads(self.sql.get(data[1]))
        if "msg" in data:
            data["msg"] = base64.b64decode(data["msg"]).decode()
        await request.sendMessage(ujson.dumps(data))
        return


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)