from botsdk.BotRequest import BotRequest
from botsdk.util.BotNotifyModule import getNotifyModule
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Cookie import getAllCookie


class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "notify"
        self.addTarget("GroupMessage", "notify", self.manageNotify)

    def init(self, bot):
        allCookie = getAllCookie()
        for i in allCookie:
            if "notify" in allCookie[i]:
                for j in allCookie[i]["notify"]:
                    getNotifyModule().addListen(i, j)

    async def manageNotify(self, request: BotRequest):
        "/notify [add/remove] 通知名"
        data = request.getFirstTextSplit()
        if len(data) < 3:
            await request.sendMessage(self.manageNotify.__doc__)
            return
        cookie = request.getCookie("notify")
        if cookie is None:
            cookie = []
        if data[1] == "add":
            if data[2] not in cookie:
                cookie.append(data[2])
                getNotifyModule().addListen(request.getId(), data[2])
                request.setCookie("notify", cookie)
        elif data[1] == "remove":
            if data[2] in cookie:
                cookie.remove(data[2])
                getNotifyModule().removeListen(data[2])
                request.setCookie("notify", cookie)
        else:
            await request.sendMessage(self.manageNotify.__doc__)
            return
        await request.sendMessage("修改完成")


def handle():
    return plugin()
