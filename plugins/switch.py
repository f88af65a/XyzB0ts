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
        if (msg := request.getFirstText()) is None and not msg:
            return True
        reData = self.pattern.search(msg)
        # target获取
        if reData is None or reData.group(4) is None:
            return True
        target = reData.group(4)
        cookie = request.getCookie("switch")
        if ((target == "enable" or target == "disable")
                and await permissionCheck(request, target)
                and (targetBot := request.getFirstText().split(" "))
                and len(targetBot) > 1):
            if targetBot not in cookie:
                cookie[targetBot] = False
            if target == "enable":
                cookie[targetBot] = True
            else:
                cookie[targetBot] = False
            request.setCookie("switch", cookie)
            await request.sendMessage("修改完成")
        return True if cookie else False
