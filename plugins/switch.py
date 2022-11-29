from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Permission import permissionCheck
from botsdk.util.JsonConfig import getConfig


class handle(BotPlugin):
    def onLoad(self):
        self.name = "switch"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addFilter(self.switchCheck)
        self.commandTarget = getConfig()["commandTarget"]

    async def switchCheck(self, request):
        if (((msg := request.getFirstText()) is None and not msg)
                or request.isSingle()
                or not request.isMessage()):
            return True
        cookie = await request.AsyncGetCookie("switch")
        if cookie is None:
            cookie = {}
        if not msg and msg[0] in self.commandTarget:
            msg = msg[1:]
            isChangeStateFlag = False
            stateFlag = False
            target = ""
            if msg.startswith("enable "):
                target = "enable"
                msg = msg[7:]
                isChangeStateFlag = True
                stateFlag = True
            if msg.startswith("disable "):
                target = "disable"
                msg = msg[8:]
                isChangeStateFlag = True
            if isChangeStateFlag and await permissionCheck(request, target):
                botName = msg
                if msg == request.getBot().getBotName():
                    cookie[botName] = stateFlag
                    await request.AsyncSetCookie("switch", cookie)
                    await request.sendMessage("修改完成")
        return True if (botName in cookie and cookie[botName]) else False
