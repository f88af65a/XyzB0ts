import json

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Cookie import getCookie, setCookie


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "cookie"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addTarget("GroupMessage", "cookie", self.cookie)
        self.addTarget("GROUP:9", "cookie", self.cookie)
        self.addTarget("FriendMessage", "cookie", self.cookie)
        self.addTarget("GroupMessage", "id", self.id)
        self.addTarget("GROUP:9", "id", self.id)
        self.addTarget("FriendMessage", "id", self.id)
        self.addTarget("GroupMessage", "acookie", self.adminCookieControl)
        self.addTarget("GROUP:9", "acookie", self.adminCookieControl)
        self.addTarget("FriendMessage", "acookie", self.adminCookieControl)
        self.addTarget("GroupMessage", "syncCookie", self.syncCookie)
        self.addTarget("GROUP:9", "syncCookie", self.syncCookie)
        self.addTarget("FriendMessage", "syncCookie", self.syncCookie)
        self.canDetach = False

    async def cookie(self, request):
        '''cookie #查看当前id所保存的cookie'''
        cookie = request.getCookie()
        await request.sendMessage(json.dumps(cookie))

    async def id(self, request):
        '''id #查看当前id'''
        await request.sendMessage(
            f"""{request.getId()} {request.getUserId()}""")

    async def adminCookieControl(self, request):
        '''acookie ID [cookie/cookie key] [cookie] #管理员cookie管理'''
        data = request.getFirstText().split(" ")
        if len(data) < 2:
            await request.sendMessage(self.adminCookieControl.__doc__)
        elif len(data) == 2:
            await request.sendMessage(str(getCookie(data[1])))
        elif len(data) == 3:
            try:
                cookieDict = json.loads(data[2])
                for i in cookieDict:
                    setCookie(data[1], i, cookieDict[i])
                await request.sendMessage("修改完成")
            except Exception:
                await request.sendMessage("参数错误")
        elif len(data) == 4:
            try:
                setCookie(data[1], data[2], json.loads(data[3]))
                await request.sendMessage("修改完成")
            except Exception:
                await request.sendMessage("参数错误")

    async def syncCookie(self, request):
        '''syncCookie DstId SrcId #同步cookie'''
        data = request.getFirstText().split(" ")
        if len(data) != 3:
            await request.sendMessage(self.syncCookie.__doc__)
            return
        SrcCookie = getCookie(data[2])
        for i in SrcCookie:
            setCookie(data[1], i, SrcCookie[i])
        await request.sendMessage("同步完成")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
