from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Permission import permissionCheck
from botsdk.util.JsonConfig import getConfig
import re


class handle(BotPlugin):
    def onLoad(self):
        self.name = "switch"
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.addFilter(self.switchCheck)
        self.canDetach = True
        self.pattern = re.compile(
            (r"^(\[(\S*=\S*)&?\])?(["
             + "".join(["\\" + i for i in getConfig()["commandTarget"]])
             + r"])(\S+)( \S+)*$"))

    async def switchCheck(self, request):
        if (((msg := request.getFirstText()) is None and not msg)
                or request.isSingle()
                or not request.isMessage()):
            return True
        reData = self.pattern.search(msg)
        # target获取
        cookie = await request.AsyncGetCookie("switch")
        if cookie is None:
            cookie = {}
        if reData is not None and reData.group(4) is not None:
            target = reData.group(4)
            if not type(cookie) is dict:
                cookie = dict()
            if ((target == "enable" or target == "disable")
                    and await permissionCheck(request, target)
                    and (targetBot := request.getFirstText().split(" "))
                    and len(targetBot) > 1):
                targetBot = targetBot[1]
                if targetBot == request.getBot().getBotName():
                    if target == "enable":
                        cookie[targetBot] = True
                    else:
                        cookie[targetBot] = False
                    request.setCookie("switch", cookie)
                    await request.sendMessage("修改完成")
        botName = request.getBot().getBotName()
        return True if (botName in cookie and cookie[botName]) else False
