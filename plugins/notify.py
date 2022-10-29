from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Cookie import getCookie, setCookie


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "notify"
        self.addTarget("GroupMessage", "notify", self.manageNotify)
        self.addBotType("Mirai")
        self.canDetach = True

    async def manageNotify(self, request):
        "notify [add/remove/list] 通知名 #监听通知"
        data = request.getFirstTextSplit()
        if len(data) == 2:
            cookie = getCookie("System:Notify")
            if cookie is None:
                cookie = {}
            if data[2] not in cookie:
                cookie[data[2]] = []
            requestId = request.getId()
            if data[1] == "list":
                haveList = []
                for i in cookie:
                    if requestId in cookie:
                        haveList.append(i)
                await request.sendMessage(str(haveList))
        elif len(data) == 3:
            cookie = getCookie("System:Notify")
            if cookie is None:
                cookie = {}
            if data[2] not in cookie:
                cookie[data[2]] = []
            requestId = request.getId()
            if data[1] == "add":
                if requestId not in cookie[data[2]]:
                    cookie[data[2]].append(requestId)
                    setCookie("System:Notify", "NotifyList", cookie)
                await request.sendMessage("修改完成")
            elif data[1] == "remove":
                if data[2] in cookie:
                    cookie.remove(data[2])
                    setCookie("System:Notify", "NotifyList", cookie)
                await request.sendMessage("修改完成")


def handle():
    return plugin()
